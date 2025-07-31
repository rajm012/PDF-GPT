import requests
import json
from typing import List, Optional, Dict, Any
import logging
import os

logger = logging.getLogger(__name__)

class LLMHandler:
    """Handles interactions with Ollama LLM"""
    
    def __init__(self, 
                 host: str = "http://localhost:11434",
                 model: str = "mistral",
                 timeout: int = 60):
        self.host = host
        self.model = model
        self.timeout = timeout
        
        # Load from environment if available
        self.host = os.getenv("OLLAMA_HOST", self.host)
        self.model = os.getenv("OLLAMA_MODEL", self.model)
    
    def check_status(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code != 200:
                return False
            
            # Check if our model is available
            models = response.json().get("models", [])
            model_names = [model.get("name", "").split(":")[0] for model in models]
            
            if self.model not in model_names:
                logger.warning(f"Model '{self.model}' not found. Available models: {model_names}")
                # Try to pull the model automatically
                self._pull_model()
            
            return True
            
        except Exception as e:
            logger.error(f"Ollama status check failed: {e}")
            return False
    
    def _pull_model(self) -> bool:
        """Pull the model if it's not available"""
        try:
            logger.info(f"Attempting to pull model: {self.model}")
            
            data = {"name": self.model}
            response = requests.post(
                f"{self.host}/api/pull",
                json=data,
                timeout=300  # 5 minutes for model download
            )
            
            if response.status_code == 200:
                logger.info(f"Model {self.model} pulled successfully")
                return True
            else:
                logger.error(f"Failed to pull model: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False
    
    def generate_answer(self, question: str, context_chunks: List[str]) -> str:
        """Generate an answer based on the question and context chunks"""
        try:
            # Prepare the context
            context = "\n\n".join(context_chunks)
            
            # Create the prompt
            prompt = self._create_prompt(question, context)
            
            # Call Ollama API
            response = self._call_ollama(prompt)
            
            if response:
                return response
            else:
                return "I apologize, but I'm having trouble generating an answer right now. Please try again."
                
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"Error generating answer: {str(e)}"
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create a well-structured prompt for the LLM"""
        prompt = f"""You are a helpful AI assistant that answers questions based on provided document content. Your task is to provide accurate, helpful answers based solely on the information given.

CONTEXT FROM DOCUMENT:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. Answer the question using ONLY the information provided in the context above
2. If the context contains specific page references or numbers mentioned in the question, prioritize that information
3. If the context doesn't contain enough information to answer the question completely, clearly state what information is missing
4. Be specific and cite relevant parts of the text when possible
5. If you quote specific parts, use quotation marks
6. Don't make up information that isn't in the context
7. If multiple relevant points exist, organize them clearly
8. For page-specific questions, focus on content that explicitly mentions that page or appears to be from that section

ANSWER:"""
        
        return prompt
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """Make API call to Ollama"""
        try:
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 1000
                }
            }
            
            response = requests.post(
                f"{self.host}/api/generate",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return "The request timed out. Please try asking a simpler question."
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama")
            return "Cannot connect to the AI service. Please ensure Ollama is running."
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            return None
    
    def summarize_text(self, text: str, max_length: int = 500) -> str:
        """Generate a summary of the provided text"""
        prompt = f"""Please provide a concise summary of the following text in about {max_length} characters or less:

TEXT TO SUMMARIZE:
{text}

SUMMARY:"""
        
        response = self._call_ollama(prompt)
        return response if response else "Could not generate summary."
    
    def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        """Extract key points from the text"""
        prompt = f"""Extract the {num_points} most important key points from the following text. Format each point as a bullet point:

TEXT:
{text}

KEY POINTS:"""
        
        response = self._call_ollama(prompt)
        
        if response:
            # Parse bullet points
            lines = response.split('\n')
            points = []
            for line in lines:
                line = line.strip()
                if line and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                    points.append(line[1:].strip())
                elif line and len(points) < num_points:
                    points.append(line)
            
            return points[:num_points]
        
        return []
    
    def generate_questions(self, text: str, num_questions: int = 5) -> List[str]:
        """Generate study questions based on the text"""
        prompt = f"""Based on the following text, generate {num_questions} thoughtful study questions that would help someone understand and remember the key concepts:

TEXT:
{text}

QUESTIONS:"""
        
        response = self._call_ollama(prompt)
        
        if response:
            # Parse questions
            lines = response.split('\n')
            questions = []
            for line in lines:
                line = line.strip()
                if line and line.endswith('?'):
                    questions.append(line)
                elif line and any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '*']):
                    # Remove numbering/bullets
                    cleaned = line
                    for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '*']:
                        if cleaned.startswith(prefix):
                            cleaned = cleaned[len(prefix):].strip()
                            break
                    if cleaned and not cleaned.endswith('?'):
                        cleaned += '?'
                    questions.append(cleaned)
            
            return questions[:num_questions]
        
        return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                current_model = None
                
                for model in models:
                    if model.get("name", "").startswith(self.model):
                        current_model = model
                        break
                
                if current_model:
                    return {
                        "name": current_model.get("name", ""),
                        "size": current_model.get("size", 0),
                        "modified_at": current_model.get("modified_at", ""),
                        "available": True
                    }
            
            return {"available": False, "error": "Model not found"}
            
        except Exception as e:
            return {"available": False, "error": str(e)}
