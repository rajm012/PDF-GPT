@echo off
echo 🚀 PDF GPT Windows Deployment
echo ==============================

REM Check if Docker is running
docker version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo ✅ Docker is running

REM Create directories
if not exist "data\uploads" mkdir data\uploads
if not exist "data\vector_db" mkdir data\vector_db
if not exist "logs" mkdir logs

REM Copy environment file if it doesn't exist
if not exist ".env.production" (
    echo ⚠️ Creating .env.production from template...
    copy .env.example .env.production
)

echo 🔨 Building Docker images...
docker-compose build

echo 🚀 Starting Ollama service...
docker-compose up -d ollama

echo ⏳ Waiting for Ollama to start...
timeout /t 10 /nobreak >nul

echo 📥 Pulling Llama3 model...
docker-compose exec ollama ollama pull llama3

echo 🚀 Starting all services...
docker-compose up -d

echo ⏳ Waiting for services to be ready...
timeout /t 15 /nobreak >nul

echo 🏥 Performing health checks...
curl -f http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Backend health check failed
) else (
    echo ✅ Backend is healthy
)

curl -f http://localhost:8501 >nul 2>&1
if errorlevel 1 (
    echo ⚠️ Frontend check failed
) else (
    echo ✅ Frontend is accessible
)

echo.
echo 🎉 Deployment complete!
echo.
echo 📱 Application URLs:
echo    Frontend: http://localhost:8501
echo    Backend API: http://localhost:5000
echo    Nginx Proxy: http://localhost:80
echo.
echo 📋 Useful commands:
echo    View logs: docker-compose logs -f
echo    Stop: docker-compose down
echo    Restart: docker-compose restart
echo.
pause
