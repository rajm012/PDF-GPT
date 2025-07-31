# PDF GPT - Chat with Your PDF/Notes

A powerful application that allows you to upload PDF documents and have intelligent conversations with their content using AI.

## 🎯 Features

- **PDF Upload & Processing**: Upload any PDF document (notes, textbooks, research papers)
- **Intelligent Chat**: Ask questions about your PDF content and get accurate answers
- **Semantic Search**: Find relevant information quickly within your documents
- **Multiple PDF Support**: Chat across multiple uploaded documents
- **Modern UI**: Clean, user-friendly Streamlit interface

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Upload UI + Chat interface)
- **Backend**: Flask (API for PDF processing and LLM requests)
- **PDF Processing**: PyMuPDF & pdfplumber (Text extraction)
- **AI/LLM**: Ollama with Mistral (Question answering)
- **Vector Search**: FAISS + LangChain (Semantic search)
- **Embeddings**: Sentence Transformers

## 🚀 Getting Started

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running locally (optional for basic functionality)
   ```bash
   # Install Ollama from https://ollama.ai/
   # Pull a model (e.g., Mistral)
   ollama pull mistral
   ```

### Installation & Setup

The project comes with a pre-configured virtual environment and all dependencies installed.

**Quick Start:**
```bash
# Start both backend and frontend
python run_app.py
```

**Manual Start (if preferred):**
1. **Start backend:**
   ```bash
   .\start_backend.bat
   ```

2. **Start frontend (in another terminal):**
   ```bash
   .\start_frontend.bat
   ```

### Using the Application

1. **Backend API**: http://localhost:5000
2. **Frontend UI**: http://localhost:8501 (opens automatically)

### First Time Setup

1. The application will automatically open in your browser
2. Upload a PDF using the sidebar file uploader
3. Click "Process PDF" to extract and index the content
4. Start chatting with your document!

## 📁 Project Structure

```
PDF-GPT/
├── frontend/
│   ├── app.py              # Streamlit UI
│   └── components/         # UI components
├── backend/
│   ├── app.py              # Flask API
│   ├── pdf_processor.py    # PDF text extraction
│   ├── llm_handler.py      # Ollama integration
│   └── vector_store.py     # FAISS/Chroma setup
├── data/
│   ├── uploads/            # Uploaded PDFs
│   └── vector_db/          # Vector database storage
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎮 How to Use

1. **Upload a PDF**: Use the file uploader in the Streamlit interface
2. **Wait for processing**: The system will extract and index the text
3. **Start chatting**: Ask questions about your PDF content
4. **Get answers**: Receive AI-powered responses with source references

## 🎁 Future Features

- 📎 PDF highlighting (show source text for answers)
- 📚 Multiple PDF chat (across documents)
- 🗣️ Voice input (Whisper integration)
- 📄 Export summaries
- 📊 Quiz generation from content

## 🐛 Troubleshooting

- **Ollama not responding**: Ensure Ollama is running (`ollama serve`)
- **PDF parsing errors**: Try with a different PDF or check file permissions
- **Memory issues**: Process smaller PDFs or increase system memory

## 📄 License

MIT License - feel free to use and modify!
