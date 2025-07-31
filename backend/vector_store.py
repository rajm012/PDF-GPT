import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available, using simple text search")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logging.warning("Sentence Transformers not available, using simple text search")

logger = logging.getLogger(__name__)

class VectorStore:
    """Handles document storage and semantic search"""
    
    def __init__(self, db_path: str = "data/vector_db"):
        self.db_path = db_path
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.chunk_metadata: Dict[int, Dict[str, Any]] = {}
        self.next_chunk_id = 0
        
        # Initialize embedding model if available
        self.embedding_model = None
        self.index = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Loaded sentence transformer model: all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"Failed to load embedding model: {e}")
        
        # Initialize FAISS index if available
        if FAISS_AVAILABLE and self.embedding_model:
            self.index = faiss.IndexFlatIP(384)  # all-MiniLM-L6-v2 has 384 dimensions
            logger.info("Initialized FAISS index")
        
        # Create database directory
        os.makedirs(db_path, exist_ok=True)
        
        # Load existing data
        self._load_data()
    
    def add_document(self, document_id: str, chunks: List[str]) -> None:
        """Add a document and its chunks to the vector store"""
        try:
            chunk_ids = []
            embeddings = []
            
            for chunk in chunks:
                chunk_id = self.next_chunk_id
                self.next_chunk_id += 1
                
                # Store chunk metadata
                self.chunk_metadata[chunk_id] = {
                    "document_id": document_id,
                    "text": chunk,
                    "timestamp": datetime.now().isoformat(),
                    "chunk_index": len(chunk_ids)
                }
                
                chunk_ids.append(chunk_id)
                
                # Generate embedding if model is available
                if self.embedding_model:
                    try:
                        embedding = self.embedding_model.encode([chunk])[0]
                        embeddings.append(embedding)
                    except Exception as e:
                        logger.warning(f"Failed to generate embedding for chunk: {e}")
                        embeddings.append(None)
            
            # Add embeddings to FAISS index
            if self.index and embeddings and all(e is not None for e in embeddings):
                embeddings_array = np.array(embeddings).astype(np.float32)
                # Normalize for cosine similarity
                faiss.normalize_L2(embeddings_array)
                self.index.add(embeddings_array)
            
            # Store document metadata
            self.documents[document_id] = {
                "id": document_id,
                "chunk_ids": chunk_ids,
                "chunk_count": len(chunks),
                "added_at": datetime.now().isoformat(),
                "has_embeddings": bool(self.embedding_model and embeddings)
            }
            
            logger.info(f"Added document {document_id} with {len(chunks)} chunks")
            
            # Save to disk
            self._save_data()
            
        except Exception as e:
            logger.error(f"Error adding document {document_id}: {e}")
            raise
    
    def search(self, document_id: str, query: str, top_k: int = 5) -> List[str]:
        """Search for relevant chunks in a document"""
        try:
            if document_id not in self.documents:
                logger.warning(f"Document {document_id} not found")
                return []
            
            doc_info = self.documents[document_id]
            chunk_ids = doc_info["chunk_ids"]
            
            # If we have embeddings and FAISS, use semantic search
            if (self.embedding_model and self.index and 
                doc_info.get("has_embeddings", False)):
                return self._semantic_search(chunk_ids, query, top_k)
            else:
                # Fall back to simple text search
                return self._text_search(chunk_ids, query, top_k)
                
        except Exception as e:
            logger.error(f"Error searching document {document_id}: {e}")
            return []
    
    def _semantic_search(self, chunk_ids: List[int], query: str, top_k: int) -> List[str]:
        """Perform semantic search using embeddings"""
        try:
            logger.info(f"Semantic search for document with {len(chunk_ids)} chunks")
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0]
            query_embedding = np.array([query_embedding]).astype(np.float32)
            faiss.normalize_L2(query_embedding)
            
            # Get all chunks for this document and their embeddings
            document_chunks = []
            document_embeddings = []
            
            for chunk_id in chunk_ids:
                if chunk_id in self.chunk_metadata:
                    chunk_text = self.chunk_metadata[chunk_id]["text"]
                    document_chunks.append(chunk_text)
                    
                    # Generate embedding for this chunk
                    try:
                        chunk_embedding = self.embedding_model.encode([chunk_text])[0]
                        document_embeddings.append(chunk_embedding)
                    except Exception as e:
                        logger.warning(f"Failed to generate embedding for chunk {chunk_id}: {e}")
                        continue
            
            if not document_embeddings:
                logger.warning("No embeddings generated, falling back to text search")
                return self._text_search(chunk_ids, query, top_k)
            
            # Calculate similarities manually
            document_embeddings = np.array(document_embeddings).astype(np.float32)
            faiss.normalize_L2(document_embeddings)
            
            # Calculate cosine similarity
            similarities = np.dot(document_embeddings, query_embedding)
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            results = [document_chunks[i] for i in top_indices if similarities[i] > 0.1]  # Minimum similarity threshold
            
            logger.info(f"Semantic search found {len(results)} relevant chunks")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            # Fall back to text search
            return self._text_search(chunk_ids, query, top_k)
    
    def _text_search(self, chunk_ids: List[int], query: str, top_k: int) -> List[str]:
        """Perform simple text-based search"""
        try:
            logger.info(f"Text search for document with {len(chunk_ids)} chunks, query: '{query}'")
            
            query_words = set(query.lower().split())
            results = []
            
            # Special handling for page-specific queries
            page_numbers = []
            import re
            page_matches = re.findall(r'page\s*(\d+)', query.lower())
            if page_matches:
                page_numbers = [int(p) for p in page_matches]
                logger.info(f"Page-specific search detected: {page_numbers}")
            
            for chunk_id in chunk_ids:
                if chunk_id in self.chunk_metadata:
                    chunk_text = self.chunk_metadata[chunk_id]["text"]
                    chunk_words = set(chunk_text.lower().split())
                    chunk_lower = chunk_text.lower()
                    
                    score = 0
                    
                    # High priority for page number matches
                    if page_numbers:
                        for page_num in page_numbers:
                            page_patterns = [
                                f"page {page_num}",
                                f"--- page {page_num} ---",
                                f"page: {page_num}",
                                f"p. {page_num}",
                                f"pg {page_num}"
                            ]
                            for pattern in page_patterns:
                                if pattern in chunk_lower:
                                    score += 10.0  # Very high score for page matches
                                    logger.info(f"Found page {page_num} match in chunk {chunk_id}")
                    
                    # Regular word overlap scoring
                    overlap = len(query_words & chunk_words)
                    if overlap > 0:
                        # Boost score if query words appear as phrase
                        phrase_boost = 1.0
                        query_lower = query.lower()
                        
                        if query_lower in chunk_lower:
                            phrase_boost = 3.0
                        elif any(word in chunk_lower for word in query_words if len(word) > 3):
                            phrase_boost = 2.0
                        
                        score += (overlap / len(query_words)) * phrase_boost
                    
                    # Contextual scoring for financial/investment terms
                    financial_terms = ['investment', 'stock', 'market', 'profit', 'earnings', 'investor', 'capital', 'dividend']
                    if any(term in query.lower() for term in financial_terms):
                        chunk_financial_score = sum(1 for term in financial_terms if term in chunk_lower)
                        score += chunk_financial_score * 0.2
                    
                    if score > 0:
                        results.append({
                            "chunk_id": chunk_id,
                            "text": chunk_text,
                            "score": score
                        })
            
            # If no good matches, do broader contextual search
            if not results or max(r["score"] for r in results) < 1.0:
                logger.info("No strong matches found, using broader contextual search")
                
                # Look for numbers, chapters, sections mentioned in query
                numbers = re.findall(r'\b\d+\b', query.lower())
                context_words = ['chapter', 'section', 'part', 'page', 'book', 'author', 'graham', 'benjamin']
                
                for chunk_id in chunk_ids:
                    if chunk_id in self.chunk_metadata:
                        chunk_text = self.chunk_metadata[chunk_id]["text"]
                        chunk_lower = chunk_text.lower()
                        
                        context_score = 0
                        
                        # Check for numbers (could be page numbers, chapter numbers, etc.)
                        for num in numbers:
                            if f" {num} " in chunk_lower or f"page {num}" in chunk_lower:
                                context_score += 1.0
                        
                        # Check for context words
                        for word in context_words:
                            if word in query.lower() and word in chunk_lower:
                                context_score += 0.5
                        
                        # Check for content richness (longer chunks might be more informative)
                        if len(chunk_text) > 200:
                            context_score += 0.1
                        
                        if context_score > 0:
                            # Only add if not already in results
                            if not any(r["chunk_id"] == chunk_id for r in results):
                                results.append({
                                    "chunk_id": chunk_id,
                                    "text": chunk_text,
                                    "score": context_score
                                })
            
            # Sort by score and return top_k
            results.sort(key=lambda x: x["score"], reverse=True)
            found_texts = [r["text"] for r in results[:top_k]]
            
            logger.info(f"Text search found {len(found_texts)} relevant chunks (scores: {[round(r['score'], 2) for r in results[:top_k]]})")
            return found_texts
            
        except Exception as e:
            logger.error(f"Text search failed: {e}")
            # Final fallback: return first few chunks
            fallback_chunks = []
            for chunk_id in chunk_ids[:top_k]:
                if chunk_id in self.chunk_metadata:
                    fallback_chunks.append(self.chunk_metadata[chunk_id]["text"])
            logger.info(f"Using fallback: returning first {len(fallback_chunks)} chunks")
            return fallback_chunks
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks"""
        try:
            if document_id not in self.documents:
                return False
            
            doc_info = self.documents[document_id]
            chunk_ids = doc_info["chunk_ids"]
            
            # Remove chunk metadata
            for chunk_id in chunk_ids:
                if chunk_id in self.chunk_metadata:
                    del self.chunk_metadata[chunk_id]
            
            # Remove document
            del self.documents[document_id]
            
            # Note: FAISS doesn't support deletion, so we'd need to rebuild the index
            # For now, we'll just remove the metadata
            
            logger.info(f"Deleted document {document_id}")
            
            # Save to disk
            self._save_data()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a document"""
        return self.documents.get(document_id)
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the vector store"""
        return list(self.documents.values())
    
    def _save_data(self) -> None:
        """Save vector store data to disk"""
        try:
            # Save metadata
            metadata_path = os.path.join(self.db_path, "metadata.pkl")
            with open(metadata_path, "wb") as f:
                pickle.dump({
                    "documents": self.documents,
                    "chunk_metadata": self.chunk_metadata,
                    "next_chunk_id": self.next_chunk_id
                }, f)
            
            # Save FAISS index if available
            if self.index:
                index_path = os.path.join(self.db_path, "faiss.index")
                faiss.write_index(self.index, index_path)
            
            logger.debug("Saved vector store data to disk")
            
        except Exception as e:
            logger.error(f"Error saving vector store data: {e}")
    
    def _load_data(self) -> None:
        """Load vector store data from disk"""
        try:
            metadata_path = os.path.join(self.db_path, "metadata.pkl")
            
            if os.path.exists(metadata_path):
                with open(metadata_path, "rb") as f:
                    data = pickle.load(f)
                    
                self.documents = data.get("documents", {})
                self.chunk_metadata = data.get("chunk_metadata", {})
                self.next_chunk_id = data.get("next_chunk_id", 0)
                
                logger.info(f"Loaded {len(self.documents)} documents from disk")
            
            # Load FAISS index if available
            index_path = os.path.join(self.db_path, "faiss.index")
            if os.path.exists(index_path) and FAISS_AVAILABLE:
                try:
                    self.index = faiss.read_index(index_path)
                    logger.info("Loaded FAISS index from disk")
                except Exception as e:
                    logger.warning(f"Failed to load FAISS index: {e}")
                    if self.embedding_model:
                        self.index = faiss.IndexFlatIP(384)
            
        except Exception as e:
            logger.error(f"Error loading vector store data: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        total_chunks = len(self.chunk_metadata)
        total_documents = len(self.documents)
        
        stats = {
            "total_documents": total_documents,
            "total_chunks": total_chunks,
            "has_embeddings": bool(self.embedding_model),
            "has_faiss": bool(self.index),
            "embedding_model": "all-MiniLM-L6-v2" if self.embedding_model else None
        }
        
        if total_documents > 0:
            avg_chunks = total_chunks / total_documents
            stats["avg_chunks_per_document"] = round(avg_chunks, 2)
        
        return stats
