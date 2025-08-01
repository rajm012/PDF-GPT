import re
import requests
from typing import Optional, Tuple

def is_page_specific_query(question: str) -> Tuple[bool, Optional[int]]:
    """Check if a question is asking about a specific page"""
    # Look for patterns like "page 21", "explain page 5", "what's on page 10"
    patterns = [
        r'page\s*(\d+)',
        r'p\.?\s*(\d+)',
        r'pg\.?\s*(\d+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, question.lower())
        if match:
            page_num = int(match.group(1))
            return True, page_num
    
    return False, None

def enhanced_chat_with_pdf(document_id: str, question: str, api_base: str = "http://127.0.0.1:5000") -> Optional[dict]:
    """Enhanced chat function that handles page-specific queries"""
    try:
        # Check if it's a page-specific query
        is_page_query, page_number = is_page_specific_query(question)
        
        if is_page_query and page_number:
            # Use page-specific endpoint
            data = {
                "document_id": document_id,
                "question": question,
                "page_number": page_number
            }
            response = requests.post(f"{api_base}/chat/page", json=data)
        else:
            # Use regular chat endpoint
            data = {
                "document_id": document_id,
                "question": question
            }
            response = requests.post(f"{api_base}/chat", json=data)
        
        if response.status_code == 200:
            result = response.json()
            # Add metadata about the query type
            result["query_type"] = "page_specific" if is_page_query else "general"
            if is_page_query:
                result["detected_page"] = page_number
            return result
        else:
            return {"error": f"API error: {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

def format_response_with_context(response: dict) -> str:
    """Format the response with better context"""
    if "error" in response:
        return f"❌ Error: {response['error']}"
    
    answer = response.get("answer", "No answer provided")
    sources = response.get("sources", [])
    query_type = response.get("query_type", "general")
    
    formatted = answer
    
    if query_type == "page_specific":
        page_num = response.get("detected_page")
        if page_num:
            formatted = f"**Page {page_num} Content:**\n\n{answer}"
    
    return formatted
