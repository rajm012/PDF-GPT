try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not found. Please install with: pip install PyMuPDF")
    raise

import pdfplumber
from typing import List, Optional
import re
import logging

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles PDF text extraction and processing"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF using both PyMuPDF and pdfplumber for best results
        """
        text_content = ""
        
        try:
            # First try PyMuPDF (faster, good for most PDFs)
            text_content = self._extract_with_pymupdf(pdf_path)
            
            # If PyMuPDF didn't get much text, try pdfplumber (better for complex layouts)
            if len(text_content.strip()) < 100:
                logger.info("PyMuPDF extracted minimal text, trying pdfplumber...")
                text_content = self._extract_with_pdfplumber(pdf_path)
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            raise
        
        # Clean up the text
        text_content = self._clean_text(text_content)
        
        logger.info(f"Extracted {len(text_content)} characters from PDF")
        return text_content
    
    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF"""
        text_content = ""
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # Add page break marker
                text_content += f"\n--- Page {page_num + 1} ---\n"
                text_content += text + "\n"
            
            doc.close()
            
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            raise
        
        return text_content
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber (better for tables and complex layouts)"""
        text_content = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    
                    if text:
                        # Add page break marker
                        text_content += f"\n--- Page {page_num + 1} ---\n"
                        text_content += text + "\n"
                    
                    # Also try to extract tables
                    tables = page.extract_tables()
                    for table in tables:
                        text_content += self._table_to_text(table)
        
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {e}")
            raise
        
        return text_content
    
    def _table_to_text(self, table: List[List[str]]) -> str:
        """Convert table data to readable text"""
        if not table:
            return ""
        
        text = "\n[TABLE DATA]\n"
        for row in table:
            if row:  # Skip empty rows
                cleaned_row = [cell if cell else "" for cell in row]
                text += " | ".join(cleaned_row) + "\n"
        text += "[END TABLE]\n"
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Remove common PDF artifacts
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
        
        # Fix common issues
        text = text.replace('\u2019', "'")  # Right single quotation mark
        text = text.replace('\u2018', "'")  # Left single quotation mark
        text = text.replace('\u201c', '"')  # Left double quotation mark
        text = text.replace('\u201d', '"')  # Right double quotation mark
        text = text.replace('\u2013', '-')  # En dash
        text = text.replace('\u2014', '--') # Em dash
        
        return text.strip()
    
    def create_chunks(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks for better context preservation
        """
        if not text:
            return []
        
        # Split by sentences first to avoid breaking mid-sentence
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = ""
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence would exceed chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + sentence
                current_length = len(current_chunk)
            else:
                current_chunk += sentence
                current_length += sentence_length
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Filter out very small chunks
        chunks = [chunk for chunk in chunks if len(chunk.strip()) > 50]
        
        logger.info(f"Created {len(chunks)} chunks from text")
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be improved with spaCy or NLTK)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() + ' ' for s in sentences if s.strip()]
    
    def _get_overlap_text(self, text: str) -> str:
        """Get the last part of text for overlap"""
        if len(text) <= self.chunk_overlap:
            return text
        
        # Try to find a good breaking point (end of sentence)
        overlap_text = text[-self.chunk_overlap:]
        sentence_end = overlap_text.rfind('. ')
        
        if sentence_end > self.chunk_overlap // 2:
            return overlap_text[sentence_end + 2:]
        else:
            return overlap_text
    
    def get_document_info(self, pdf_path: str) -> dict:
        """Get basic information about the PDF"""
        try:
            doc = fitz.open(pdf_path)
            
            info = {
                "page_count": len(doc),
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "modification_date": doc.metadata.get("modDate", "")
            }
            
            doc.close()
            return info
            
        except Exception as e:
            logger.error(f"Error getting PDF info: {e}")
            return {"error": str(e)}
