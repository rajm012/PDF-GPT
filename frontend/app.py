import streamlit as st
import requests
import os
from typing import Optional
import time
import re

# Import our enhanced chat utilities
from chat_utils import enhanced_chat_with_pdf, format_response_with_context

# Configure page
st.set_page_config(
    page_title="PDF GPT - Chat with Your Documents",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API URL
API_BASE = "http://127.0.0.1:5000"

def upload_pdf(file) -> Optional[str]:
    """Upload PDF to backend and return document ID"""
    try:
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        response = requests.post(f"{API_BASE}/upload", files=files)
        
        if response.status_code == 200:
            return response.json().get("document_id")
        else:
            st.error(f"Upload failed: {response.json().get('error', 'Unknown error')}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Please ensure Flask server is running.")
        return None
    except Exception as e:
        st.error(f"❌ Upload error: {str(e)}")
        return None

def chat_with_pdf(document_id: str, question: str) -> Optional[dict]:
    """Send question to backend and get AI response"""
    try:
        # Use enhanced chat function
        return enhanced_chat_with_pdf(document_id, question, API_BASE)
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Please ensure Flask server is running.")
        return None
    except Exception as e:
        st.error(f"❌ Chat error: {str(e)}")
        return None

def main():
    # Header
    st.title("📚 PDF GPT - Chat with Your Documents")
    st.markdown("Upload a PDF and have intelligent conversations with its content!")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Upload Document")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload your PDF document to start chatting with it"
        )
        
        if uploaded_file is not None:
            st.success(f"📄 **{uploaded_file.name}** ready for upload")
            
            if st.button("🚀 Process PDF", type="primary"):
                with st.spinner("Processing PDF... This may take a moment."):
                    document_id = upload_pdf(uploaded_file)
                    
                    if document_id:
                        st.session_state.document_id = document_id
                        st.session_state.document_name = uploaded_file.name
                        st.success("✅ PDF processed successfully!")
                        st.rerun()
        
        # Show current document
        if "document_id" in st.session_state:
            st.markdown("---")
            st.markdown("**📄 Current Document:**")
            st.info(st.session_state.document_name)
            
            if st.button("🗑️ Clear Document"):
                del st.session_state.document_id
                del st.session_state.document_name
                if "messages" in st.session_state:
                    del st.session_state.messages
                st.rerun()
    
    # Main chat interface
    if "document_id" not in st.session_state:
        # Welcome screen
        st.markdown("""
        ## 🎯 How to Get Started
        
        1. **📁 Upload a PDF** using the sidebar
        2. **⚡ Process the document** by clicking "Process PDF"
        3. **💬 Start chatting** with your document!
        
        ### 📚 What You Can Ask
        - *"Summarize the main points"*
        - *"Explain chapter 3 in simple terms"*
        - *"What's on page 25?"*
        - *"Tell me about page 50"*
        - *"What does the author say about [topic]?"*
        - *"List the key findings"*
        - *"Generate questions about this content"*
        
        ### 🛠️ Features
        - ✅ **Smart PDF Processing** - Extracts and indexes text
        - ✅ **AI-Powered Answers** - Uses Ollama LLM for responses
        - ✅ **Semantic Search** - Finds relevant sections quickly
        - ✅ **Source References** - Shows where answers come from
        """)
        
        # System status check
        st.markdown("---")
        st.markdown("### 🔧 System Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            try:
                response = requests.get(f"{API_BASE}/health", timeout=3)
                if response.status_code == 200:
                    st.success("✅ Backend API: Online")
                else:
                    st.error("❌ Backend API: Error")
            except:
                st.error("❌ Backend API: Offline")
        
        with col2:
            try:
                response = requests.get(f"{API_BASE}/ollama-status", timeout=5)
                if response.status_code == 200 and response.json().get("status") == "ready":
                    st.success("✅ Ollama LLM: Ready")
                else:
                    st.warning("⚠️ Ollama LLM: Not Ready")
            except:
                st.error("❌ Ollama LLM: Offline")
    
    else:
        # Chat interface
        st.markdown(f"### 💬 Chat with **{st.session_state.document_name}**")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant", 
                    "content": f"Hello! I've processed your document **{st.session_state.document_name}**. What would you like to know about it?"
                }
            ]
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Show sources if available
                if message["role"] == "assistant" and "sources" in message:
                    with st.expander("📖 Source References"):
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(f"**Source {i}:** {source}")
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your document..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = chat_with_pdf(st.session_state.document_id, prompt)
                    
                    if response:
                        answer = response.get("answer", "Sorry, I couldn't generate an answer.")
                        sources = response.get("sources", [])
                        query_type = response.get("query_type", "general")
                        detected_page = response.get("detected_page")
                        
                        # Format answer with enhanced context
                        if query_type == "page_specific" and detected_page:
                            formatted_answer = f"**Page {detected_page} Content:**\n\n{answer}"
                        else:
                            formatted_answer = answer
                        
                        st.markdown(formatted_answer)
                        
                        # Show sources with better formatting
                        if sources:
                            with st.expander("📖 Source References"):
                                for i, source in enumerate(sources, 1):
                                    st.markdown(f"**Source {i}:**")
                                    # Check if source contains page markers
                                    if "--- page" in source.lower():
                                        st.markdown(f"*{source}*")
                                    else:
                                        st.markdown(f"{source}")
                                    st.markdown("---")
                        
                        # Add metadata info for debugging
                        if query_type == "page_specific":
                            st.info(f"🔍 Detected page-specific query for page {detected_page}")
                        
                        # Add to session state
                        assistant_message = {
                            "role": "assistant", 
                            "content": formatted_answer,
                            "query_type": query_type
                        }
                        if sources:
                            assistant_message["sources"] = sources
                        
                        st.session_state.messages.append(assistant_message)
                    else:
                        error_msg = "❌ Sorry, I couldn't process your question. Please try again."
                        st.markdown(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": error_msg
                        })

if __name__ == "__main__":
    main()
