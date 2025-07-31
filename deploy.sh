#!/bin/bash

# PDF GPT Deployment Script

set -e

echo "🚀 PDF GPT Deployment Script"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Docker and Docker Compose are installed."
}

# Check if Ollama model is available
setup_ollama() {
    print_status "Setting up Ollama..."
    
    # Start Ollama container first
    docker-compose up -d ollama
    
    # Wait for Ollama to be ready
    print_status "Waiting for Ollama to start..."
    sleep 10
    
    # Pull the required model
    print_status "Pulling Llama3 model..."
    docker-compose exec ollama ollama pull llama3
    
    print_status "Ollama setup complete."
}

# Build and deploy
deploy() {
    print_status "Building Docker images..."
    docker-compose build
    
    print_status "Starting all services..."
    docker-compose up -d
    
    print_status "Waiting for services to be ready..."
    sleep 15
    
    # Health check
    print_status "Performing health checks..."
    
    # Check backend
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        print_status "✅ Backend is healthy"
    else
        print_warning "⚠️ Backend health check failed"
    fi
    
    # Check frontend
    if curl -f http://localhost:8501 > /dev/null 2>&1; then
        print_status "✅ Frontend is accessible"
    else
        print_warning "⚠️ Frontend accessibility check failed"
    fi
}

# Main deployment function
main() {
    echo "Starting deployment process..."
    
    # Check prerequisites
    check_docker
    
    # Setup environment
    if [ ! -f .env.production ]; then
        print_warning ".env.production not found, creating from template..."
        cp .env.example .env.production
    fi
    
    # Create data directories
    mkdir -p data/uploads data/vector_db logs
    
    # Setup Ollama
    setup_ollama
    
    # Deploy application
    deploy
    
    print_status "🎉 Deployment complete!"
    echo ""
    echo "📱 Application URLs:"
    echo "   Frontend: http://localhost:8501"
    echo "   Backend API: http://localhost:5000"
    echo "   Nginx Proxy: http://localhost:80"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop: docker-compose down"
    echo "   Restart: docker-compose restart"
    echo ""
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        print_status "Stopping all services..."
        docker-compose down
        ;;
    "restart")
        print_status "Restarting all services..."
        docker-compose restart
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "status")
        docker-compose ps
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status}"
        exit 1
        ;;
esac
