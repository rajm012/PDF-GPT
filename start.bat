@echo off
REM Production deployment startup script with TOML configuration support

echo 🚀 Starting PDF GPT Application with TOML Configuration...

REM Check if config.toml exists
if exist "config.toml" (
    echo ✅ Found config.toml - Using TOML configuration
    set CONFIG_MODE=toml
) else (
    echo ⚠️ No config.toml found - Using environment variables
    set CONFIG_MODE=env
    
    REM Set default environment variables if not already set
    if not defined SECRET_KEY set SECRET_KEY=your-production-secret-key-here
    if not defined FLASK_ENV set FLASK_ENV=production
    if not defined UPLOAD_FOLDER set UPLOAD_FOLDER=data/uploads
    if not defined VECTOR_DB_PATH set VECTOR_DB_PATH=data/vector_db
    if not defined MAX_FILE_SIZE set MAX_FILE_SIZE=50
    if not defined CHUNK_SIZE set CHUNK_SIZE=1000
    if not defined CHUNK_OVERLAP set CHUNK_OVERLAP=200
    if not defined OLLAMA_HOST set OLLAMA_HOST=http://localhost:11434
    if not defined OLLAMA_MODEL set OLLAMA_MODEL=llama3
    if not defined LOG_LEVEL set LOG_LEVEL=INFO
    if not defined LOG_FILE set LOG_FILE=logs/app.log
    if not defined WORKERS set WORKERS=4
    if not defined THREADS set THREADS=2
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "data\uploads" mkdir "data\uploads"
if not exist "data\vector_db" mkdir "data\vector_db"
if not exist "logs" mkdir "logs"

REM Check if Ollama is running
echo 🤖 Checking Ollama service...
curl -s "%OLLAMA_HOST%/api/tags" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama is running
) else (
    echo ❌ Ollama is not running. Please start Ollama first:
    echo    ollama serve
    pause
    exit /b 1
)

REM Check if the model is available
echo 🔍 Checking if model '%OLLAMA_MODEL%' is available...
ollama list | findstr /i "%OLLAMA_MODEL%" >nul
if %errorlevel% equ 0 (
    echo ✅ Model '%OLLAMA_MODEL%' is available
) else (
    echo 📥 Pulling model '%OLLAMA_MODEL%'...
    ollama pull "%OLLAMA_MODEL%"
)

REM Install Python dependencies if needed
if exist "requirements.txt" (
    echo 📦 Installing Python dependencies...
    pip install -r requirements.txt
)

REM Start the backend server
echo 🔧 Starting backend server...
cd backend

if "%FLASK_ENV%"=="production" (
    echo 🏭 Starting in production mode with Gunicorn...
    gunicorn --config gunicorn.conf.py app:app
) else (
    echo 🛠️ Starting in development mode...
    python app.py
)

pause
