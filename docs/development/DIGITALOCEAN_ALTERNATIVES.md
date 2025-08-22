# DigitalOcean Alternative Deployment Methods

Since the current Kubernetes setup has issues with DigitalOcean's load balancer health checks, here are more compatible alternatives:

## Option 1: DigitalOcean App Platform (Recommended)

### Advantages:
- **Native DigitalOcean integration**
- **Automatic SSL certificates**
- **Built-in load balancing**
- **Easy scaling**
- **No Kubernetes complexity**

### Setup:
1. **Install doctl** (if not already installed):
   ```bash
   brew install doctl
   doctl auth init
   ```

2. **Deploy to App Platform**:
   ```bash
   doctl apps create --spec .do/app.yaml
   ```

3. **Set environment variables** in DigitalOcean dashboard

## Option 2: Docker Compose on DigitalOcean Droplet

### Advantages:
- **Simpler than Kubernetes**
- **Full control over configuration**
- **Easy to debug**
- **Cost-effective**

### Setup:
1. **Create a DigitalOcean Droplet** with Docker pre-installed
2. **Upload files** to the droplet
3. **Set environment variables**:
   ```bash
   cp env.production .env
   # Edit .env with your actual values
   ```

4. **Deploy with Docker Compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

5. **Configure SSL** with Let's Encrypt:
   ```bash
   sudo apt install certbot
   sudo certbot --nginx -d kolekt.io -d www.kolekt.io
   ```

## Option 3: Fix Current Kubernetes Setup

### Issues to Address:
1. **Health check port mismatch** (32249 vs 80/443)
2. **PROXY protocol configuration**
3. **Node health status**

### Quick Fix Attempt:
```bash
# Update health check configuration
kubectl patch service ingress-nginx-controller -n ingress-nginx \
  --type='json' \
  -p='[{"op": "add", "path": "/metadata/annotations/service.beta.kubernetes.io~1do-loadbalancer-healthcheck-path", "value": "/healthz"}]'
```

## Recommendation

**Use DigitalOcean App Platform** for the easiest and most reliable deployment. It's specifically designed for DigitalOcean and handles SSL, load balancing, and scaling automatically.

## Migration Steps

1. **Export current environment variables** from Kubernetes secrets
2. **Deploy to App Platform** using the `.do/app.yaml` configuration
3. **Update DNS** to point to the new App Platform URL
4. **Test the application**
5. **Clean up Kubernetes resources** (optional)

## Environment Variables Needed

Make sure these are set in your chosen deployment method:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `META_APP_ID`
- `META_APP_SECRET`
- `THREADS_APP_ID`
- `THREADS_APP_SECRET`
- `SECRET_KEY`
- `TOKEN_ENCRYPTION_KEY`
- `REDIS_PASSWORD`
