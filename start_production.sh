#!/bin/bash

echo "🚀 Starting PDF GPT Production Server..."

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '#' | xargs)
fi

# Create necessary directories
mkdir -p /app/data/uploads /app/data/vector_db /app/logs

# Function to start backend
start_backend() {
    echo "Starting Flask Backend..."
    cd /app/backend
    gunicorn --bind 0.0.0.0:${FLASK_PORT:-5000} \
             --workers ${WORKERS:-4} \
             --threads ${THREADS:-2} \
             --timeout 120 \
             --access-logfile /app/logs/access.log \
             --error-logfile /app/logs/error.log \
             --log-level ${LOG_LEVEL:-info} \
             app:app &
    BACKEND_PID=$!
    echo "Backend started with PID: $BACKEND_PID"
}

# Function to start frontend
start_frontend() {
    echo "Starting Streamlit Frontend..."
    cd /app
    streamlit run frontend/app.py \
        --server.port ${STREAMLIT_PORT:-8501} \
        --server.address 0.0.0.0 \
        --server.headless true \
        --browser.gatherUsageStats false &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
}

# Cleanup function
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap for cleanup
trap cleanup SIGTERM SIGINT

# Start services
start_backend
sleep 5
start_frontend

# Wait for processes
wait
