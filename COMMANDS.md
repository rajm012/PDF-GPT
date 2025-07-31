# PDF GPT Quick Commands

## Development Commands
```bash
# Start development environment
python run_app.py

# Start services individually
.\start_backend.bat
.\start_frontend.bat

# Test backend
python test_backend.py

# Health check
python health_check.py
```

## Production Commands
```bash
# Deploy with Docker
./deploy.sh               # Linux/Mac
deploy.bat                # Windows

# Manual Docker commands
docker-compose build
docker-compose up -d
docker-compose logs -f
docker-compose down

# Scale services
docker-compose up -d --scale backend=3

# Update deployment
git pull origin main
docker-compose build
docker-compose up -d
```

## Maintenance Commands
```bash
# View logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs ollama

# Backup data
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Clean up
docker-compose down -v
docker system prune -a

# Restart services
docker-compose restart
docker-compose restart backend
```

## Environment Management
```bash
# Development
export FLASK_ENV=development
export LOG_LEVEL=DEBUG

# Production
export FLASK_ENV=production
export LOG_LEVEL=INFO

# Copy environment template
cp .env.example .env.production
```

## Troubleshooting
```bash
# Check service status
docker-compose ps

# Inspect containers
docker-compose exec backend bash
docker-compose exec frontend bash

# Check resource usage
docker stats

# Reset everything
docker-compose down -v
rm -rf data/vector_db/*
docker-compose up -d
```
