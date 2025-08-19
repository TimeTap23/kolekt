# ThreadStorm Kubernetes Deployment Guide

## 🎯 **Complete Kubernetes Deployment for ThreadStorm**

This guide provides step-by-step instructions for deploying ThreadStorm to Kubernetes with monitoring, scaling, and production-ready features.

## 📋 **Prerequisites**

### **Required Tools**
- ✅ **kubectl** - Kubernetes command-line tool
- ✅ **Docker** - Container runtime
- ✅ **Kubernetes cluster** - Local (minikube/kind) or cloud (EKS/GKE/AKS)
- ✅ **Git** - Version control

### **Cluster Requirements**
- **CPU**: 4+ cores
- **RAM**: 8GB+ 
- **Storage**: 50GB+ available
- **Kubernetes version**: 1.24+

## 🚀 **Quick Start Deployment**

### **Step 1: Prepare Environment**
```bash
# Clone repository (if not already done)
git clone https://github.com/your-username/threadstorm.git
cd threadstorm

# Create production environment
cp env.production .env.production
# Edit .env.production with your actual values
```

### **Step 2: Encode Secrets**
```bash
# Run the secrets encoder
./k8s/encode-secrets.sh

# Copy the encoded values to k8s/secrets.yaml
# Replace placeholder values with actual encoded values
```

### **Step 3: Deploy to Kubernetes**
```bash
# Complete deployment
./k8s/deploy.sh deploy
```

## 🔧 **Detailed Deployment Steps**

### **1. Environment Configuration**

Create your production environment file:

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

# Optional: Monitoring
SENTRY_DSN=your-sentry-dsn
SLACK_WEBHOOK_URL=your-slack-webhook
DISCORD_WEBHOOK_URL=your-discord-webhook
```

### **2. Secrets Management**

Encode your secrets for Kubernetes:

```bash
./k8s/encode-secrets.sh
```

This will output encoded values like:
```yaml
supabase-url: aHR0cHM6Ly95b3VyLXByb2plY3Quc3VwYWJhc2UuY28=
supabase-key: eW91ci1zdXBhYmFzZS1hbm9uLWtleQ==
# ... more encoded values
```

Copy these values to `k8s/secrets.yaml`, replacing the placeholder values.

### **3. Build and Push Docker Image**

```bash
# Build the image
docker build -t ghcr.io/your-username/threadstorm:latest .

# Push to registry
docker push ghcr.io/your-username/threadstorm:latest
```

**Note**: Update the image name in `k8s/deployment.yaml` to match your registry.

### **4. Deploy to Kubernetes**

#### **Option A: Complete Deployment**
```bash
./k8s/deploy.sh deploy
```

#### **Option B: Step-by-Step Deployment**
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl apply -f k8s/secrets.yaml

# Deploy Redis
kubectl apply -f k8s/redis.yaml

# Deploy ThreadStorm
kubectl apply -f k8s/deployment.yaml

# Deploy monitoring (optional)
kubectl apply -f k8s/monitoring.yaml
```

### **5. Verify Deployment**

```bash
# Check all resources
kubectl get all -n threadstorm

# Check pod status
kubectl get pods -n threadstorm

# Check services
kubectl get services -n threadstorm

# Check ingress
kubectl get ingress -n threadstorm
```

## 📊 **Monitoring Setup**

### **Deploy Monitoring Stack**
```bash
kubectl apply -f k8s/monitoring.yaml
```

### **Access Monitoring Tools**

#### **Prometheus**
```bash
# Port forward to access Prometheus
kubectl port-forward service/prometheus-service 9090:9090 -n threadstorm
```
Access: http://localhost:9090

#### **Grafana**
```bash
# Port forward to access Grafana
kubectl port-forward service/grafana-service 3000:3000 -n threadstorm
```
Access: http://localhost:3000
- Username: `admin`
- Password: Set in secrets (grafana-password)

## 🔍 **Deployment Management**

### **Check Deployment Status**
```bash
./k8s/deploy.sh status
```

### **View Application Logs**
```bash
./k8s/deploy.sh logs
```

### **Scale Deployment**
```bash
# Scale to 5 replicas
./k8s/deploy.sh scale 5

# Or use kubectl directly
kubectl scale deployment threadstorm --replicas=5 -n threadstorm
```

### **Upgrade Deployment**
```bash
# Build and push new image
docker build -t ghcr.io/your-username/threadstorm:latest .
docker push ghcr.io/your-username/threadstorm:latest

# Upgrade deployment
./k8s/deploy.sh upgrade
```

### **Health Check**
```bash
./k8s/deploy.sh health
```

## 🌐 **Accessing the Application**

### **Get Service URLs**
```bash
# Get LoadBalancer IP
kubectl get service threadstorm-service -n threadstorm

# Get Ingress information
kubectl get ingress threadstorm-ingress -n threadstorm
```

### **Port Forwarding (for local access)**
```bash
# Forward main application
kubectl port-forward service/threadstorm-service 8000:80 -n threadstorm

# Forward admin panel
kubectl port-forward service/threadstorm-service 8001:80 -n threadstorm
```

### **Access URLs**
- **Main Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs

## 🔒 **Security Configuration**

### **SSL/TLS Setup**

#### **Option A: Let's Encrypt (Recommended)**
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

#### **Option B: Self-Signed Certificates**
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout tls.key -out tls.crt \
    -subj "/CN=threadstorm.com"

# Create TLS secret
kubectl create secret tls threadstorm-tls \
    --key tls.key --cert tls.crt \
    -n threadstorm
```

### **Network Policies**
```bash
# Apply network policies for security
kubectl apply -f k8s/network-policies.yaml
```

## 📈 **Scaling and Performance**

### **Horizontal Pod Autoscaler**
The HPA is already configured in `k8s/deployment.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: threadstorm-hpa
spec:
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### **Resource Limits**
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### **Vertical Scaling**
To increase resource limits:

```bash
# Edit deployment
kubectl edit deployment threadstorm -n threadstorm

# Or update the YAML file and reapply
kubectl apply -f k8s/deployment.yaml
```

## 🔄 **Backup and Recovery**

### **Database Backup**
```bash
# Supabase handles backups automatically
# For manual backup:
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

### **Application Backup**
```bash
# Backup configuration
tar -czf threadstorm_k8s_backup_$(date +%Y%m%d).tar.gz \
    k8s/ .env.production
```

### **Disaster Recovery**
```bash
# Restore from backup
tar -xzf threadstorm_k8s_backup_20241201.tar.gz
kubectl apply -f k8s/
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Pods Not Starting**
```bash
# Check pod status
kubectl get pods -n threadstorm

# Check pod events
kubectl describe pod <pod-name> -n threadstorm

# Check pod logs
kubectl logs <pod-name> -n threadstorm
```

#### **2. Services Not Accessible**
```bash
# Check service status
kubectl get services -n threadstorm

# Check endpoints
kubectl get endpoints -n threadstorm

# Test service connectivity
kubectl run test-pod --image=busybox -it --rm --restart=Never -- nslookup threadstorm-service
```

#### **3. Ingress Issues**
```bash
# Check ingress status
kubectl get ingress -n threadstorm

# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

#### **4. Resource Issues**
```bash
# Check resource usage
kubectl top pods -n threadstorm

# Check node resources
kubectl top nodes

# Check events
kubectl get events -n threadstorm --sort-by='.lastTimestamp'
```

### **Debug Commands**
```bash
# Get all resources in namespace
kubectl get all -n threadstorm

# Check configuration
kubectl get configmaps -n threadstorm
kubectl get secrets -n threadstorm

# Check persistent volumes
kubectl get pvc -n threadstorm
kubectl get pv

# Check HPA status
kubectl get hpa -n threadstorm
kubectl describe hpa threadstorm-hpa -n threadstorm
```

## 🎯 **Production Checklist**

### **Before Going Live**
- [ ] **Environment variables** configured
- [ ] **Secrets** properly encoded and applied
- [ ] **SSL certificates** configured
- [ ] **Domain DNS** pointing to cluster
- [ ] **Monitoring** stack deployed
- [ ] **Backup strategy** implemented
- [ ] **Resource limits** appropriate
- [ ] **Security policies** applied
- [ ] **Load testing** completed
- [ ] **Documentation** updated

### **Post-Deployment**
- [ ] **Health checks** passing
- [ ] **Monitoring dashboards** working
- [ ] **Logs** being collected
- [ ] **Alerts** configured
- [ ] **Performance** meeting expectations
- [ ] **Security** verified
- [ ] **Backup** tested

## 📞 **Support and Maintenance**

### **Regular Maintenance**
```bash
# Update images
./k8s/deploy.sh upgrade

# Check resource usage
kubectl top pods -n threadstorm

# Review logs
kubectl logs -f deployment/threadstorm -n threadstorm

# Monitor HPA
kubectl get hpa -n threadstorm
```

### **Useful Commands**
```bash
# Quick status check
./k8s/deploy.sh status

# View logs
./k8s/deploy.sh logs

# Health check
./k8s/deploy.sh health

# Scale deployment
./k8s/deploy.sh scale 5

# Delete deployment
./k8s/deploy.sh delete
```

## 🎉 **Success Metrics**

### **Deployment Success Indicators**
- ✅ **All pods running** - `kubectl get pods -n threadstorm`
- ✅ **Services accessible** - Health checks passing
- ✅ **Ingress working** - SSL certificates valid
- ✅ **Monitoring active** - Prometheus/Grafana accessible
- ✅ **Auto-scaling ready** - HPA configured
- ✅ **Backup working** - Data protection verified

### **Performance Indicators**
- **Response time**: < 200ms average
- **Uptime**: 99.9% availability
- **Resource usage**: < 80% CPU/Memory
- **Error rate**: < 1% 5xx errors
- **Throughput**: 1000+ requests/second

---

## 🚀 **ThreadStorm Kubernetes Deployment Complete!**

Your ThreadStorm application is now running on Kubernetes with:
- ✅ **High availability** - Multiple replicas with auto-scaling
- ✅ **Load balancing** - Ingress with SSL termination
- ✅ **Monitoring** - Prometheus and Grafana
- ✅ **Security** - Network policies and secrets management
- ✅ **Scalability** - Horizontal and vertical scaling
- ✅ **Backup** - Data protection and recovery

**ThreadStorm is ready for production use!** 🎉
