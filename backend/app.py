from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List
import logging

# Import our custom modules
from pdf_processor import PDFProcessor
from llm_handler import LLMHandler
from vector_store import VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = "data/uploads"
VECTOR_DB_PATH = "data/vector_db"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

# Initialize components
pdf_processor = PDFProcessor()
llm_handler = LLMHandler()
vector_store = VectorStore(VECTOR_DB_PATH)

# Store document metadata
documents: Dict[str, Dict[str, Any]] = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "documents_loaded": len(documents)
    }), 200

@app.route('/ollama-status', methods=['GET'])
def ollama_status():
    """Check if Ollama is available"""
    try:
        status = llm_handler.check_status()
        return jsonify({"status": "ready" if status else "not_ready"}), 200
    except Exception as e:
        logger.error(f"Ollama status check failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Upload and process a PDF document"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({"error": f"File too large. Max size: {MAX_FILE_SIZE // 1024 // 1024}MB"}), 400
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Save file
        filename = f"{document_id}_{file.filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        logger.info(f"Saved file: {filepath}")
        
        # Process PDF
        try:
            text_content = pdf_processor.extract_text(filepath)
            if not text_content.strip():
                return jsonify({"error": "Could not extract text from PDF"}), 400
            
            # Create text chunks
            chunks = pdf_processor.create_chunks(text_content)
            logger.info(f"Created {len(chunks)} chunks from PDF")
            
            # Store in vector database
            vector_store.add_document(document_id, chunks)
            
            # Store document metadata
            documents[document_id] = {
                "id": document_id,
                "filename": file.filename,
                "filepath": filepath,
                "upload_time": datetime.now().isoformat(),
                "chunk_count": len(chunks),
                "text_length": len(text_content)
            }
            
            logger.info(f"Successfully processed document {document_id}")
            
            return jsonify({
                "document_id": document_id,
                "filename": file.filename,
                "chunks": len(chunks),
                "status": "processed"
            }), 200
            
        except Exception as e:
            # Clean up file if processing failed
            if os.path.exists(filepath):
                os.remove(filepath)
            logger.error(f"PDF processing failed: {e}")
            return jsonify({"error": f"PDF processing failed: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat/page', methods=['POST'])
def chat_page_specific():
    """Chat with specific focus on page numbers"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        document_id = data.get('document_id')
        question = data.get('question')
        page_number = data.get('page_number')
        
        if not document_id or not question:
            return jsonify({"error": "document_id and question are required"}), 400
        
        # Check if document exists
        if document_id not in documents:
            return jsonify({"error": "Document not found"}), 404
        
        # Modify question to include page reference if provided
        if page_number:
            enhanced_question = f"page {page_number} {question}"
        else:
            enhanced_question = question
        
        try:
            # Search with enhanced page-focused query
            relevant_chunks = vector_store.search(document_id, enhanced_question, top_k=3)
            logger.info(f"Page-specific search found {len(relevant_chunks)} chunks for: '{enhanced_question}'")
            
            if not relevant_chunks:
                return jsonify({
                    "answer": f"I couldn't find content specifically related to page {page_number or 'the requested page'}. The document might not have clear page markers, or the page might not be in the processed content.",
                    "sources": [],
                    "page_number": page_number
                }), 200
            
            # Generate answer with page context
            answer = llm_handler.generate_answer(enhanced_question, relevant_chunks)
            
            # Format sources with focus on page relevance
            sources = []
            for chunk in relevant_chunks:
                if page_number and f"page {page_number}" in chunk.lower():
                    # Prioritize chunks that explicitly mention the page
                    sources.insert(0, chunk[:300] + "..." if len(chunk) > 300 else chunk)
                else:
                    sources.append(chunk[:250] + "..." if len(chunk) > 250 else chunk)
            
            return jsonify({
                "answer": answer,
                "sources": sources,
                "document_id": document_id,
                "page_number": page_number
            }), 200
            
        except Exception as e:
            logger.error(f"Page-specific chat error: {e}")
            return jsonify({"error": f"Failed to process page-specific question: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Page chat error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Chat with a processed document"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        document_id = data.get('document_id')
        question = data.get('question')
        
        if not document_id or not question:
            return jsonify({"error": "document_id and question are required"}), 400
        
        # Check if document exists
        if document_id not in documents:
            return jsonify({"error": "Document not found"}), 404
        
        # Get relevant chunks from vector store
        try:
            relevant_chunks = vector_store.search(document_id, question, top_k=5)
            logger.info(f"Found {len(relevant_chunks)} relevant chunks for question: '{question}'")
            
            # If no chunks found, try a broader search or return first few chunks
            if not relevant_chunks:
                logger.warning(f"No chunks found for question: '{question}', trying fallback")
                
                # Fallback: get first few chunks of the document
                doc_info = documents[document_id]
                if hasattr(vector_store, 'chunk_metadata'):
                    fallback_chunks = []
                    for chunk_id, metadata in vector_store.chunk_metadata.items():
                        if metadata.get('document_id') == document_id and len(fallback_chunks) < 3:
                            fallback_chunks.append(metadata['text'])
                    
                    if fallback_chunks:
                        logger.info(f"Using {len(fallback_chunks)} fallback chunks")
                        relevant_chunks = fallback_chunks
                
                # If still no chunks, return informative message
                if not relevant_chunks:
                    return jsonify({
                        "answer": "I couldn't find relevant information in the document to answer your question. This might be due to the document structure or search terms. Please try rephrasing your question or asking about general content.",
                        "sources": [],
                        "debug_info": f"Document has {doc_info.get('chunk_count', 0)} chunks processed"
                    }), 200
            
            # Generate answer using LLM
            answer = llm_handler.generate_answer(question, relevant_chunks)
            
            # Format sources - prioritize more relevant/specific ones
            sources = []
            for i, chunk in enumerate(relevant_chunks):
                # Truncate long chunks but try to keep the most relevant part
                if len(chunk) > 300:
                    # Try to find the most relevant sentence
                    sentences = chunk.split('. ')
                    best_sentence = ""
                    query_words = set(question.lower().split())
                    
                    max_overlap = 0
                    for sentence in sentences:
                        sentence_words = set(sentence.lower().split())
                        overlap = len(query_words & sentence_words)
                        if overlap > max_overlap:
                            max_overlap = overlap
                            best_sentence = sentence
                    
                    if best_sentence and len(best_sentence) < 200:
                        source_text = best_sentence + "..."
                    else:
                        source_text = chunk[:250] + "..."
                else:
                    source_text = chunk
                
                sources.append(source_text)
            
            return jsonify({
                "answer": answer,
                "sources": sources,
                "document_id": document_id
            }), 200
            
        except Exception as e:
            logger.error(f"Chat processing error: {e}")
            return jsonify({"error": f"Failed to process question: {str(e)}"}), 500
            
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/documents/<document_id>/debug', methods=['GET'])
def debug_document(document_id):
    """Debug endpoint to check document chunks"""
    try:
        if document_id not in documents:
            return jsonify({"error": "Document not found"}), 404
        
        doc_info = documents[document_id]
        
        # Get document stats from vector store
        vector_stats = vector_store.get_document_info(document_id)
        
        # Get first few chunks for preview
        chunk_ids = doc_info.get('chunk_count', 0)
        sample_chunks = []
        
        if hasattr(vector_store, 'chunk_metadata'):
            # Get first 3 chunks as sample
            for chunk_id in list(vector_store.chunk_metadata.keys())[:3]:
                if vector_store.chunk_metadata[chunk_id].get('document_id') == document_id:
                    chunk_text = vector_store.chunk_metadata[chunk_id]['text']
                    sample_chunks.append(chunk_text[:300] + "..." if len(chunk_text) > 300 else chunk_text)
        
        return jsonify({
            "document_info": doc_info,
            "vector_store_info": vector_stats,
            "total_chunks_in_metadata": len([k for k, v in vector_store.chunk_metadata.items() if v.get('document_id') == document_id]) if hasattr(vector_store, 'chunk_metadata') else 0,
            "sample_chunks": sample_chunks
        }), 200
        
    except Exception as e:
        logger.error(f"Debug error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/documents', methods=['GET'])
def list_documents():
    """List all processed documents"""
    return jsonify({
        "documents": list(documents.values()),
        "count": len(documents)
    }), 200

@app.route('/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Delete a processed document"""
    try:
        if document_id not in documents:
            return jsonify({"error": "Document not found"}), 404
        
        # Remove from vector store
        vector_store.delete_document(document_id)
        
        # Remove file
        doc_info = documents[document_id]
        if os.path.exists(doc_info['filepath']):
            os.remove(doc_info['filepath'])
        
        # Remove from memory
        del documents[document_id]
        
        return jsonify({"message": "Document deleted successfully"}), 200
        
    except Exception as e:
        logger.error(f"Delete error: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "File too large"}), 413

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("🚀 Starting PDF GPT Backend Server...")
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🗄️ Vector DB path: {VECTOR_DB_PATH}")
    print("🔗 Backend will be available at: http://127.0.0.1:5000")
    print("💡 Make sure Ollama is running for LLM functionality!")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
