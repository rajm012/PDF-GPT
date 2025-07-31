# 🚀 PDF GPT Deployment Guide

This guide covers deploying PDF GPT in various environments: local development, Docker containers, cloud platforms, and production servers.

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.8+** (for manual deployment)
- **Git** for cloning
- **8GB+ RAM** (for running Ollama models)

## 🐳 Docker Deployment (Recommended)

### Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd PDF-GPT

# Deploy with one command
./deploy.sh
# or on Windows:
deploy.bat
```

### Manual Docker Steps

```bash
# 1. Create environment file
cp .env.example .env.production
# Edit .env.production with your settings

# 2. Build and start services
docker-compose up -d

# 3. Setup Ollama model
docker-compose exec ollama ollama pull llama3

# 4. Check status
docker-compose ps
```

### Service URLs
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:5000  
- **Nginx Proxy**: http://localhost:80

## 🔧 Manual Deployment

### Backend Setup

```bash
# 1. Install dependencies
pip install -r requirements-prod.txt

# 2. Set environment
export FLASK_ENV=production
export OLLAMA_HOST=http://localhost:11434

# 3. Create directories
mkdir -p data/uploads data/vector_db logs

# 4. Start with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 backend.app:app
```

### Frontend Setup

```bash
# Start Streamlit
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

## ☁️ Cloud Deployment

### AWS ECS/Fargate

1. **Push to ECR**:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t pdf-gpt .
docker tag pdf-gpt:latest <account>.dkr.ecr.us-east-1.amazonaws.com/pdf-gpt:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/pdf-gpt:latest
```

2. **Create ECS Task Definition** with:
   - Frontend container (port 8501)
   - Backend container (port 5000)
   - Ollama container (port 11434)
   - Shared EFS volume for data

### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/pdf-gpt
gcloud run deploy --image gcr.io/PROJECT_ID/pdf-gpt --platform managed
```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name pdf-gpt \
  --image myregistry.azurecr.io/pdf-gpt:latest \
  --ports 8501 5000
```

## 🔒 Production Security

### Environment Variables

```bash
# Required for production
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
FLASK_ENV=production

# Optional security
RATE_LIMIT_ENABLED=true
MAX_UPLOADS_PER_HOUR=10
```

### SSL/HTTPS Setup

1. **Get SSL Certificate**:
```bash
# Using Let's Encrypt
certbot certonly --webroot -w /var/www/html -d yourdomain.com
```

2. **Update nginx.conf**:
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    # ... rest of config
}
```

## 📊 Monitoring & Logging

### Health Checks

```bash
# Backend health
curl http://localhost:5000/health

# Ollama status  
curl http://localhost:11434/api/tags

# Frontend check
curl http://localhost:8501
```

### Log Locations

- **Application logs**: `/app/logs/app.log`
- **Access logs**: `/app/logs/access.log`
- **Error logs**: `/app/logs/error.log`
- **Docker logs**: `docker-compose logs -f`

## 🎯 Performance Optimization

### Resource Limits

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: 2.0
```

### Scaling

```bash
# Scale backend instances
docker-compose up -d --scale backend=3

# Load balancer configuration needed
```

## 🛠️ Maintenance

### Backup Data

```bash
# Backup vector database
tar -czf backup-$(date +%Y%m%d).tar.gz data/vector_db/

# Backup uploaded files
tar -czf uploads-$(date +%Y%m%d).tar.gz data/uploads/
```

### Update Deployment

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d

# Check status
docker-compose ps
```

### Database Migration

```bash
# If vector database format changes
docker-compose exec backend python scripts/migrate_db.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Ollama not responding**:
```bash
docker-compose restart ollama
docker-compose exec ollama ollama pull llama3
```

2. **Frontend can't connect to backend**:
```bash
# Check backend logs
docker-compose logs backend

# Verify network connectivity
docker-compose exec frontend curl http://backend:5000/health
```

3. **Out of memory**:
```bash
# Check resource usage
docker stats

# Reduce Ollama model size or increase RAM
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose restart
```

## 📱 Mobile/Responsive Access

The Streamlit frontend is responsive and works on mobile devices. For better mobile experience:

1. **PWA Support**: Add to your phone's home screen
2. **Mobile optimizations**: Built into Streamlit
3. **Touch-friendly**: Large buttons and inputs

## 🚀 Advanced Features

### Redis Session Storage

```yaml
# Add to docker-compose.yml
redis:
  image: redis:alpine
  ports:
    - "6379:6379"
```

### Multiple Model Support

```bash
# Pull multiple models
docker-compose exec ollama ollama pull llama3
docker-compose exec ollama ollama pull mistral
docker-compose exec ollama ollama pull codellama
```

### API Authentication

Add JWT tokens or API keys for production use.

---

## 🎉 Success!

Your PDF GPT application should now be running in production! 

- 📱 **Frontend**: http://localhost:8501
- 🔧 **Backend**: http://localhost:5000
- 📋 **Health**: http://localhost:5000/health

For support, check the logs and refer to this guide.
