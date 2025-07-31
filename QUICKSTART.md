# PDF GPT Quick Start Guide

## Prerequisites

1. **Install Python 3.8+**
2. **Install Ollama:**
   - Visit https://ollama.ai/ and download for your OS
   - Run: `ollama pull mistral` (or your preferred model)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment (optional):**
   ```bash
   copy .env.example .env
   # Edit .env if needed
   ```

## Running the Application

### Option 1: Use the startup script (Recommended)
```bash
python start.py
```

### Option 2: Manual startup
1. **Start backend:**
   ```bash
   python backend/app.py
   ```

2. **Start frontend (in another terminal):**
   ```bash
   streamlit run frontend/app.py
   ```

## Usage

1. Open http://localhost:8501 in your browser
2. Upload a PDF using the sidebar
3. Click "Process PDF" 
4. Start chatting with your document!

## Troubleshooting

- **"Cannot connect to backend"**: Make sure Flask server is running
- **"Ollama not ready"**: Ensure Ollama is installed and running (`ollama serve`)
- **PDF processing errors**: Try a different PDF or check file permissions
- **Memory issues**: Process smaller PDFs or increase system memory

## Features

- 📄 PDF text extraction
- 🤖 AI-powered Q&A
- 🔍 Semantic search
- 💬 Chat interface
- 📚 Multiple document support
