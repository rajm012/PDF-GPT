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
   ollama pull llama3
   ```

### Quick Start (Development)

**Option 1: All-in-One Launcher**
```bash
python run_app.py
```

**Option 2: Manual Start**
```bash
# Terminal 1: Backend
.\start_backend.bat

# Terminal 2: Frontend  
.\start_frontend.bat
```

### Production Deployment 🐳

**Docker Deployment (Recommended)**
```bash
# One-command deployment
./deploy.sh
# or on Windows:
deploy.bat

# Manual Docker steps
docker-compose up -d
```

**Manual Production Setup**
```bash
# Install production dependencies
pip install -r requirements-prod.txt

# Set environment
export FLASK_ENV=production

# Start with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 backend.app:app
```

### 📱 Application URLs

- **Development**: http://localhost:8501
- **Production Frontend**: http://localhost:8501  
- **Backend API**: http://localhost:5000
- **Nginx Proxy**: http://localhost:80

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

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

## 🚀 Deployment Ready

### Production Features
- **🐳 Docker Support**: Complete containerization with docker-compose
- **🔧 Production Config**: Gunicorn, Nginx, environment management
- **📊 Monitoring**: Health checks, logging, and error tracking
- **🔒 Security**: Rate limiting, CORS, file validation
- **⚡ Performance**: Multi-worker setup, caching, optimization
- **☁️ Cloud Ready**: AWS, GCP, Azure deployment guides

### Scaling Options
- **Multi-instance**: Docker Compose scaling
- **Load Balancing**: Nginx reverse proxy
- **Database**: Persistent vector storage
- **Session Management**: Redis integration

## 🐛 Troubleshooting

- **Ollama not responding**: Ensure Ollama is running (`ollama serve`)
- **PDF parsing errors**: Try with a different PDF or check file permissions
- **Memory issues**: Process smaller PDFs or increase system memory

## 📄 License

MIT License - feel free to use and modify!
