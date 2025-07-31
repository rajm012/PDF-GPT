#!/bin/bash
# Production deployment startup script with TOML configuration support

echo "🚀 Starting PDF GPT Application with TOML Configuration..."

# Check if config.toml exists
if [ -f "config.toml" ]; then
    echo "✅ Found config.toml - Using TOML configuration"
    export CONFIG_MODE="toml"
else
    echo "⚠️ No config.toml found - Using environment variables"
    export CONFIG_MODE="env"
    
    # Set default environment variables if not already set
    export SECRET_KEY=${SECRET_KEY:-"your-production-secret-key-here"}
    export FLASK_ENV=${FLASK_ENV:-"production"}
    export UPLOAD_FOLDER=${UPLOAD_FOLDER:-"data/uploads"}
    export VECTOR_DB_PATH=${VECTOR_DB_PATH:-"data/vector_db"}
    export MAX_FILE_SIZE=${MAX_FILE_SIZE:-"50"}
    export CHUNK_SIZE=${CHUNK_SIZE:-"1000"}
    export CHUNK_OVERLAP=${CHUNK_OVERLAP:-"200"}
    export OLLAMA_HOST=${OLLAMA_HOST:-"http://localhost:11434"}
    export OLLAMA_MODEL=${OLLAMA_MODEL:-"llama3"}
    export LOG_LEVEL=${LOG_LEVEL:-"INFO"}
    export LOG_FILE=${LOG_FILE:-"logs/app.log"}
    export WORKERS=${WORKERS:-"4"}
    export THREADS=${THREADS:-"2"}
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/uploads
mkdir -p data/vector_db
mkdir -p logs

# Check if Ollama is running
echo "🤖 Checking Ollama service..."
if curl -s "${OLLAMA_HOST:-http://localhost:11434}/api/tags" > /dev/null; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama is not running. Please start Ollama first:"
    echo "   ollama serve"
    exit 1
fi

# Check if the model is available
echo "🔍 Checking if model '${OLLAMA_MODEL:-llama3}' is available..."
if ollama list | grep -q "${OLLAMA_MODEL:-llama3}"; then
    echo "✅ Model '${OLLAMA_MODEL:-llama3}' is available"
else
    echo "📥 Pulling model '${OLLAMA_MODEL:-llama3}'..."
    ollama pull "${OLLAMA_MODEL:-llama3}"
fi

# Install Python dependencies if needed
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start the backend server
echo "🔧 Starting backend server..."
cd backend

if [ "$FLASK_ENV" = "production" ]; then
    echo "🏭 Starting in production mode with Gunicorn..."
    gunicorn --config gunicorn.conf.py app:app
else
    echo "🛠️ Starting in development mode..."
    python app.py
fi
