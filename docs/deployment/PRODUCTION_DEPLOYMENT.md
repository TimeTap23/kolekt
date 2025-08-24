# Kolekt Production Deployment Guide

This guide covers the complete production deployment of Kolekt using multiple deployment strategies.

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended for small to medium scale)

```bash
# 1. Clone the repository
git clone https://github.com/your-username/kolekt.git
cd kolekt

# 2. Configure environment
cp env.production .env.production
# Edit .env.production with your actual values

# 3. Deploy
./deploy.sh deploy
```

### Option 2: Kubernetes (Recommended for large scale)

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create secrets
kubectl apply -f k8s/secrets.yaml

# 3. Deploy Redis
kubectl apply -f k8s/redis.yaml

# 4. Deploy Kolekt
kubectl apply -f k8s/deployment.yaml
```

## 📋 Prerequisites

### System Requirements

- **CPU**: 2+ cores
- **RAM**: 4GB+ 
- **Storage**: 20GB+ available space
- **OS**: Linux (Ubuntu 20.04+ recommended)

### Software Requirements

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: Latest version
- **OpenSSL**: For SSL certificate generation

### For Kubernetes Deployment

- **Kubernetes**: 1.24+
- **kubectl**: Latest version
- **Helm**: 3.0+ (optional)
- **NGINX Ingress Controller**: Installed
- **cert-manager**: For SSL certificates

## 🔧 Configuration

### 1. Environment Variables

Copy the production environment template:

```bash
cp env.production .env.production
```

Edit `.env.production` with your actual values:

```bash
# Required: Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Required: Security
SECRET_KEY=your-super-secret-production-key
TOKEN_ENCRYPTION_KEY=your-32-character-encryption-key

# Required: Meta/Threads API
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret
THREADS_APP_ID=your-threads-app-id
THREADS_APP_SECRET=your-threads-app-secret

# Optional: AWS KMS
AWS_KMS_KEY_ID=your-kms-key-id
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
ENABLE_KMS_ENCRYPTION=false
```

### 2. SSL Certificates

#### Option A: Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d kolekt.com -d www.kolekt.com

# Copy certificates
sudo cp /etc/letsencrypt/live/kolekt.com/fullchain.pem nginx/ssl/kolekt.crt
sudo cp /etc/letsencrypt/live/kolekt.com/privkey.pem nginx/ssl/kolekt.key
```

#### Option B: Self-Signed (Development)

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/kolekt.key \
    -out nginx/ssl/kolekt.crt \
    -subj "/C=US/ST=State/L=City/O=Kolekt/CN=kolekt.com"
```

### 3. Domain Configuration

Configure your DNS records:

```
A     kolekt.com     → Your server IP
A     www.kolekt.com → Your server IP
CNAME  api.kolekt.com → kolekt.com
```

## 🐳 Docker Compose Deployment

### 1. Basic Deployment

```bash
# Deploy all services
./deploy.sh deploy

# Check status
./deploy.sh status

# View logs
./deploy.sh logs
```

### 2. Service Management

```bash
# Stop services
./deploy.sh stop

# Restart services
./deploy.sh restart

# Health check
./deploy.sh health

# Cleanup
./deploy.sh cleanup
```

### 3. Scaling

Edit `docker-compose.yml` to scale services:

```yaml
services:
  kolekt:
    deploy:
      replicas: 3  # Scale to 3 instances
```

## ☸️ Kubernetes Deployment

### 1. Prerequisites Setup

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

### 2. Configure Secrets

Create a script to encode your secrets:

```bash
#!/bin/bash
# encode-secrets.sh

echo "Encoding secrets for Kubernetes..."

# Supabase
echo "supabase-url: $(echo -n "https://your-project.supabase.co" | base64)"
echo "supabase-key: $(echo -n "your-supabase-anon-key" | base64)"
echo "supabase-service-role-key: $(echo -n "your-supabase-service-role-key" | base64)"

# Meta/Threads
echo "meta-app-id: $(echo -n "your-meta-app-id" | base64)"
echo "meta-app-secret: $(echo -n "your-meta-app-secret" | base64)"
echo "threads-app-id: $(echo -n "your-threads-app-id" | base64)"
echo "threads-app-secret: $(echo -n "your-threads-app-secret" | base64)"

# Security
echo "secret-key: $(echo -n "your-super-secret-production-key" | base64)"
echo "token-encryption-key: $(echo -n "your-32-character-encryption-key" | base64)"

# Redis
echo "redis-password: $(echo -n "your-secure-redis-password" | base64)"
```

Update `k8s/secrets.yaml` with the encoded values.

### 3. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl apply -f k8s/secrets.yaml

# Deploy Redis
kubectl apply -f k8s/redis.yaml

# Deploy Kolekt
kubectl apply -f k8s/deployment.yaml

# Check deployment
kubectl get pods -n kolekt
kubectl get services -n kolekt
kubectl get ingress -n kolekt
```

### 4. Scaling

```bash
# Scale Kolekt deployment
kubectl scale deployment kolekt --replicas=5 -n kolekt

# Check HPA status
kubectl get hpa -n kolekt
```

## 🔄 CI/CD Pipeline

### GitHub Actions

1. **Configure Secrets** in your GitHub repository:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
       - `META_APP_ID`
    - `META_APP_SECRET`
    - `THREADS_APP_ID`
    - `THREADS_APP_SECRET`
   - `SLACK_WEBHOOK_URL` (optional)
   - `DISCORD_WEBHOOK_URL` (optional)

2. **Push to main branch** to trigger staging deployment
3. **Push to production branch** to trigger production deployment

### Manual Deployment

```bash
# Build and push Docker image
docker build -t ghcr.io/your-username/kolekt:latest .
docker push ghcr.io/your-username/kolekt:latest

# Deploy to Kubernetes
kubectl rollout restart deployment/kolekt -n kolekt
```

## 📊 Monitoring & Logging

### 1. Application Logs

```bash
# Docker Compose
docker-compose logs -f kolekt

# Kubernetes
kubectl logs -f deployment/kolekt -n kolekt
```

### 2. Health Monitoring

```bash
# Health check endpoint
curl https://kolekt.com/health

# Kubernetes health
kubectl get pods -n kolekt -o wide
kubectl describe pod <pod-name> -n kolekt
```

### 3. Performance Monitoring

```bash
# Resource usage
kubectl top pods -n kolekt
kubectl top nodes

# Metrics
kubectl get hpa -n kolekt
```

## 🔒 Security Hardening

### 1. Network Security

```bash
# Configure firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Container Security

```bash
# Run security scan
docker run --rm -v $(pwd):/app aquasec/trivy fs /app

# Update base images regularly
docker-compose pull
docker-compose up -d
```

### 3. Secret Management

```bash
# Rotate secrets regularly
# Update .env.production and redeploy
./deploy.sh restart
```

## 🚨 Troubleshooting

### Common Issues

1. **Application won't start**
   ```bash
   # Check logs
   docker-compose logs kolekt
   
   # Check environment variables
   docker-compose config
   ```

2. **Database connection issues**
   ```bash
   # Test Supabase connection
   curl -H "apikey: $SUPABASE_KEY" $SUPABASE_URL/rest/v1/
   ```

3. **SSL certificate issues**
   ```bash
   # Check certificate validity
   openssl x509 -in nginx/ssl/kolekt.crt -text -noout
   
   # Renew Let's Encrypt certificate
   sudo certbot renew
   ```

4. **Kubernetes deployment issues**
   ```bash
   # Check pod status
   kubectl describe pod <pod-name> -n kolekt
   
   # Check events
   kubectl get events -n kolekt --sort-by='.lastTimestamp'
   ```

### Performance Issues

1. **High memory usage**
   ```bash
   # Check memory usage
   docker stats
   kubectl top pods -n kolekt
   
   # Scale up resources
   # Edit docker-compose.yml or k8s/deployment.yaml
   ```

2. **Slow response times**
   ```bash
   # Check Redis connection
   docker exec -it kolekt-redis redis-cli ping
   
   # Check database performance
   # Monitor Supabase dashboard
   ```

## 📈 Scaling Strategies

### Horizontal Scaling

```bash
# Docker Compose
docker-compose up -d --scale kolekt=3

# Kubernetes
kubectl scale deployment kolekt --replicas=5 -n kolekt
```

### Vertical Scaling

```bash
# Update resource limits in docker-compose.yml or k8s/deployment.yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### Load Balancing

```bash
# Configure NGINX upstream
upstream kolekt_backend {
    server kolekt:8000 weight=1;
    server kolekt:8001 weight=1;
    server kolekt:8002 weight=1;
}
```

## 🔄 Backup & Recovery

### 1. Database Backup

```bash
# Supabase backup (automatic)
# Configure in Supabase dashboard

# Manual backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Application Backup

```bash
# Backup configuration
tar -czf kolekt_config_$(date +%Y%m%d).tar.gz \
    .env.production nginx/ssl/ logs/ uploads/
```

### 3. Disaster Recovery

```bash
# Restore from backup
tar -xzf kolekt_config_20241201.tar.gz
./deploy.sh deploy
```

## 📞 Support

For deployment issues:

1. Check the logs: `./deploy.sh logs`
2. Verify configuration: `./deploy.sh health`
3. Review this documentation
4. Check GitHub Issues
5. Contact support team

## 🎯 Next Steps

After successful deployment:

1. **Configure monitoring** (Sentry, DataDog, etc.)
2. **Set up alerts** for critical issues
3. **Implement backup automation**
4. **Configure CDN** for static assets
5. **Set up staging environment**
6. **Implement blue-green deployments**

---

**Kolekt Production Deployment Complete! 🚀**

Your application is now running in production with:
- ✅ High availability
- ✅ SSL encryption
- ✅ Load balancing
- ✅ Auto-scaling
- ✅ Monitoring
- ✅ Backup strategy
