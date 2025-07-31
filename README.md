# PDF GPT - Chat with Your PDF/Notes 📚🤖

A powerful AI-powered application that allows you to upload PDF documents and have intelligent conversations with them using local LLM through Ollama.

## 🚀 Features

- **PDF Upload & Processing**: Support for various PDF formats with robust text extraction
- **Intelligent Chat**: Ask questions about your PDFs and get contextual answers
- **Page-Specific Queries**: Search for information from specific pages
- **Semantic Search**: Advanced vector-based search using FAISS
- **Local AI**: Powered by Ollama for privacy and offline usage
- **Production Ready**: Docker support with nginx reverse proxy
- **Flexible Configuration**: Support for both TOML files and environment variables

## 🏗️ Architecture

- **Frontend**: Streamlit application for user interface
- **Backend**: Flask API server for PDF processing and chat
- **AI Engine**: Ollama with llama3 model for natural language processing
- **Vector Database**: FAISS for semantic search
- **PDF Processing**: PyMuPDF + pdfplumber for robust text extraction

## 📋 Prerequisites

- Python 3.8+ 
- [Ollama](https://ollama.ai/) installed and running
- Docker & Docker Compose (for production deployment)

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd PDF-GPT
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install and Setup Ollama
```bash
# Install Ollama (visit https://ollama.ai for installation instructions)

# Start Ollama service
ollama serve

# Pull the llama3 model
ollama pull llama3
```

## ⚙️ Configuration

The application supports two configuration methods:

### Method 1: TOML Configuration (Recommended)

Create a `config.toml` file in the root directory:

```toml
[app]
SECRET_KEY = "your-production-secret-key-change-this"
FLASK_ENV = "production"
DEBUG = false

[server]
HOST = "0.0.0.0"
PORT = 5000
WORKERS = 4
THREADS = 2

[storage]
UPLOAD_FOLDER = "data/uploads"
VECTOR_DB_PATH = "data/vector_db"
MAX_FILE_SIZE = 50  # MB

[security]
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "your-domain.com"]
CORS_ORIGINS = ["http://localhost:8501", "https://your-domain.com"]

[logging]
LOG_LEVEL = "INFO"
LOG_FILE = "logs/app.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

[performance]
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
VECTOR_STORE_TYPE = "faiss"

[features]
ENABLE_RATE_LIMITING = true
MAX_UPLOADS_PER_HOUR = 10
ENABLE_PAGE_SEARCH = true
ENABLE_SEMANTIC_SEARCH = true

[ai]
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MAX_CONTEXT_LENGTH = 4000

[database]
VECTOR_SIMILARITY_THRESHOLD = 0.7
MAX_SEARCH_RESULTS = 5
```

### Method 2: Environment Variables

Alternatively, you can use environment variables:

```bash
export SECRET_KEY="your-production-secret-key"
export FLASK_ENV="production"
export UPLOAD_FOLDER="data/uploads"
export VECTOR_DB_PATH="data/vector_db"
export MAX_FILE_SIZE="50"
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_MODEL="llama3"
export LOG_LEVEL="INFO"
# ... other variables
```

## 🚀 Running the Application

### Development Mode

1. **Start the Backend**:
```bash
cd backend
python app.py
```

2. **Start the Frontend** (in a new terminal):
```bash
cd frontend
streamlit run app.py
```

3. **Access the Application**:
- Frontend: http://localhost:8501
- Backend API: http://localhost:5000

### Production Mode with Docker

1. **Using Docker Compose**:
```bash
docker-compose up -d
```

2. **Using Startup Scripts**:
```bash
# Linux/Mac
./start.sh

# Windows
start.bat
```

3. **Manual Production Setup**:
```bash
cd backend
gunicorn --config gunicorn.conf.py app:app
```

## 📖 Usage

1. **Upload a PDF**: Click "Choose a PDF file" and upload your document
2. **Ask Questions**: Type your questions in the chat interface
3. **Page-Specific Queries**: Use phrases like "on page 5" or "from page 10" for targeted search
4. **View Results**: Get contextual answers with page references

### Example Queries
- "What is the main topic of this document?"
- "Summarize page 3"
- "What does the author say about artificial intelligence on page 15?"
- "Find information about machine learning"

## 🐳 Docker Deployment

### Development
```bash
docker-compose -f docker-compose.dev.yml up
```

### Production
```bash
docker-compose -f docker-compose.yml up -d
```

The production setup includes:
- Nginx reverse proxy with SSL support
- Rate limiting and security headers
- Health checks and restart policies
- Volume mounts for persistent data

## 🔧 API Endpoints

### Backend API (Flask)

- `POST /upload` - Upload and process PDF
- `POST /chat` - General chat with document
- `POST /chat/page` - Page-specific chat
- `GET /health` - Health check
- `GET /debug/chunks` - Debug: View document chunks
- `GET /debug/search` - Debug: Test search functionality

### Frontend (Streamlit)

- Main interface: http://localhost:8501
- Upload interface and chat interface combined

## 🗂️ Project Structure

```
PDF-GPT/
├── frontend/
│   ├── app.py              # Streamlit UI
│   ├── chat_utils.py       # Chat utility functions
│   └── requirements.txt    # Frontend dependencies
├── backend/
│   ├── app.py              # Flask API server
│   ├── config_loader.py    # TOML/Environment config loader
│   ├── pdf_processor.py    # PDF text extraction
│   ├── llm_handler.py      # Ollama integration
│   ├── vector_store.py     # FAISS vector search
│   ├── gunicorn.conf.py    # Production server config
│   └── requirements.txt    # Backend dependencies
├── data/
│   ├── uploads/            # Uploaded PDF files
│   └── vector_db/          # Vector database storage
├── logs/                   # Application logs
├── config.toml             # TOML configuration file
├── docker-compose.yml      # Production Docker setup
├── docker-compose.dev.yml  # Development Docker setup
├── nginx.conf              # Nginx configuration
├── Dockerfile              # Docker image definition
├── start.sh               # Linux/Mac startup script
├── start.bat              # Windows startup script
└── requirements.txt        # Root dependencies
```

## 🐛 Troubleshooting

### Common Issues

1. **Ollama Connection Error**:
   - Ensure Ollama is running: `ollama serve`
   - Check the correct host in config: `OLLAMA_HOST=http://localhost:11434`

2. **Model Not Found**:
   - Pull the model: `ollama pull llama3`
   - Verify available models: `ollama list`

3. **PDF Processing Errors**:
   - Check file size limits in config
   - Ensure PDF is not password protected
   - Try different PDF files to isolate the issue

4. **Search Not Working**:
   - Check debug endpoints: `GET /debug/chunks` and `GET /debug/search`
   - Verify vector database is created in `data/vector_db/`
   - Check logs for embedding errors

5. **Configuration Issues**:
   - Verify TOML syntax: use a TOML validator
   - Check environment variable names (case-sensitive)
   - Ensure all required directories exist

### Debug Mode

Enable debug mode by setting:
```toml
[app]
DEBUG = true
FLASK_ENV = "development"

[logging]
LOG_LEVEL = "DEBUG"
```

Or with environment variables:
```bash
export DEBUG=true
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
```

## 🔒 Security Considerations

### Production Deployment

1. **Change Default Secret Key**:
   ```toml
   [app]
   SECRET_KEY = "your-strong-random-secret-key"
   ```

2. **Configure Allowed Hosts**:
   ```toml
   [security]
   ALLOWED_HOSTS = ["your-domain.com"]
   CORS_ORIGINS = ["https://your-domain.com"]
   ```

3. **Enable Rate Limiting**:
   ```toml
   [features]
   ENABLE_RATE_LIMITING = true
   MAX_UPLOADS_PER_HOUR = 10
   ```

4. **SSL/TLS Configuration**:
   - Use the provided nginx.conf with SSL certificates
   - Redirect HTTP to HTTPS

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM inference
- [Streamlit](https://streamlit.io/) for the intuitive UI framework
- [LangChain](https://langchain.com/) for LLM orchestration
- [FAISS](https://github.com/facebookresearch/faiss) for efficient vector search
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing

---

**Happy chatting with your PDFs! 📚✨**
