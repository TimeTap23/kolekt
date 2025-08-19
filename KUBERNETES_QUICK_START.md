# ThreadStorm Kubernetes Quick Start

## 🚀 **Quick Setup Guide**

This guide provides the fastest way to get ThreadStorm running on Kubernetes.

## 📋 **Prerequisites**

- ✅ **Docker Desktop** installed and running
- ✅ **kubectl** installed
- ✅ **Git** for cloning the repository

## ⚡ **5-Minute Setup (Local Development)**

### **Step 1: Enable Kubernetes in Docker Desktop**
1. Open Docker Desktop
2. Go to Settings → Kubernetes
3. Check "Enable Kubernetes"
4. Click "Apply & Restart"
5. Wait for Kubernetes to start

### **Step 2: Run Setup Script**
```bash
# Clone repository (if not already done)
git clone https://github.com/your-username/threadstorm.git
cd threadstorm

# Run automated setup
./setup-kubernetes.sh local
```

### **Step 3: Configure Environment**
```bash
# Edit production environment
nano .env.production

# Encode secrets
./k8s/encode-secrets.sh
```

### **Step 4: Deploy ThreadStorm**
```bash
# Deploy everything
./k8s/deploy.sh deploy

# Access application
kubectl port-forward service/threadstorm-service 8000:80 -n threadstorm
```

### **Step 5: Access Your Application**
- **Main App**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Health Check**: http://localhost:8000/health

## ☁️ **Cloud Deployment (Production)**

### **AWS EKS**
```bash
# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create cluster
eksctl create cluster --name threadstorm-cluster --region us-west-2 --node-type t3.medium --nodes 3

# Deploy ThreadStorm
./k8s/deploy.sh deploy
```

### **Google GKE**
```bash
# Install gcloud
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Create cluster
gcloud container clusters create threadstorm-cluster --zone us-central1-a --num-nodes 3

# Deploy ThreadStorm
./k8s/deploy.sh deploy
```

### **Azure AKS**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login

# Create cluster
az aks create --resource-group threadstorm-rg --name threadstorm-cluster --node-count 3

# Deploy ThreadStorm
./k8s/deploy.sh deploy
```

## 🔧 **Essential Commands**

### **Deployment Management**
```bash
# Check status
./k8s/deploy.sh status

# View logs
./k8s/deploy.sh logs

# Scale deployment
./k8s/deploy.sh scale 5

# Upgrade deployment
./k8s/deploy.sh upgrade
```

### **Kubernetes Commands**
```bash
# Check all resources
kubectl get all -n threadstorm

# Check pods
kubectl get pods -n threadstorm

# View logs
kubectl logs -f deployment/threadstorm -n threadstorm

# Port forward
kubectl port-forward service/threadstorm-service 8000:80 -n threadstorm
```

### **Monitoring Access**
```bash
# Prometheus
kubectl port-forward service/prometheus-service 9090:9090 -n threadstorm

# Grafana
kubectl port-forward service/grafana-service 3000:3000 -n threadstorm
```

## 🔐 **Environment Configuration**

### **Required Variables**
```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# Security
SECRET_KEY=your-super-secret-production-key
TOKEN_ENCRYPTION_KEY=your-32-character-encryption-key

# Meta/Threads API
META_APP_ID=your-meta-app-id
META_APP_SECRET=your-meta-app-secret
THREADS_APP_ID=your-threads-app-id
THREADS_APP_SECRET=your-threads-app-secret
```

### **Optional Variables**
```bash
# AWS KMS (for advanced encryption)
AWS_KMS_KEY_ID=your-kms-key-id
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
SLACK_WEBHOOK_URL=your-slack-webhook
DISCORD_WEBHOOK_URL=your-discord-webhook
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Kubernetes Not Running**
```bash
# Check Docker Desktop Kubernetes
kubectl cluster-info

# If not running, enable in Docker Desktop settings
```

#### **Pods Not Starting**
```bash
# Check pod status
kubectl get pods -n threadstorm

# Check pod events
kubectl describe pod <pod-name> -n threadstorm

# Check pod logs
kubectl logs <pod-name> -n threadstorm
```

#### **Services Not Accessible**
```bash
# Check service status
kubectl get services -n threadstorm

# Check endpoints
kubectl get endpoints -n threadstorm

# Test connectivity
kubectl run test-pod --image=busybox -it --rm --restart=Never -- nslookup threadstorm-service
```

### **Debug Commands**
```bash
# Get all resources
kubectl get all -n threadstorm

# Check events
kubectl get events -n threadstorm --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n threadstorm

# Check HPA status
kubectl get hpa -n threadstorm
```

## 📊 **Monitoring Setup**

### **Access Monitoring Tools**
```bash
# Prometheus (Metrics)
kubectl port-forward service/prometheus-service 9090:9090 -n threadstorm
# Access: http://localhost:9090

# Grafana (Dashboards)
kubectl port-forward service/grafana-service 3000:3000 -n threadstorm
# Access: http://localhost:3000
# Username: admin
# Password: Set in secrets (grafana-password)
```

### **Key Metrics to Monitor**
- **Application Health**: Service status and availability
- **Response Time**: HTTP request latency
- **Error Rate**: 4xx and 5xx error rates
- **Resource Usage**: CPU and memory consumption
- **Throughput**: Requests per second

## 🎯 **Production Checklist**

### **Before Going Live**
- [ ] **Cluster created** and nodes ready
- [ ] **Environment configured** with production values
- [ ] **Secrets encoded** and applied
- [ ] **SSL certificates** configured
- [ ] **Domain DNS** pointing to cluster
- [ ] **Monitoring** stack deployed
- [ ] **Backup strategy** implemented

### **Post-Deployment Verification**
- [ ] **All pods running** - Health checks passing
- [ ] **Services accessible** - Load balancer working
- [ ] **Ingress functional** - SSL certificates valid
- [ ] **Monitoring active** - Metrics being collected
- [ ] **Auto-scaling ready** - HPA configured
- [ ] **Performance acceptable** - Response times < 200ms

## 🚀 **Quick Commands Summary**

```bash
# Complete setup (local)
./setup-kubernetes.sh local

# Configure environment
cp env.production .env.production
nano .env.production

# Encode secrets
./k8s/encode-secrets.sh

# Deploy ThreadStorm
./k8s/deploy.sh deploy

# Access application
kubectl port-forward service/threadstorm-service 8000:80 -n threadstorm

# Check status
./k8s/deploy.sh status

# View logs
./k8s/deploy.sh logs

# Scale deployment
./k8s/deploy.sh scale 5
```

## 📞 **Support**

### **Documentation**
- **Complete Setup Guide**: `KUBERNETES_SETUP_GUIDE.md`
- **Deployment Guide**: `KUBERNETES_DEPLOYMENT_GUIDE.md`
- **Troubleshooting**: See troubleshooting section above

### **Useful Resources**
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Docker Desktop**: https://www.docker.com/products/docker-desktop
- **kubectl Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/

---

## 🎉 **ThreadStorm Kubernetes Quick Start Complete!**

Your ThreadStorm application is now running on Kubernetes with:
- ✅ **High availability** - Multiple replicas with auto-scaling
- ✅ **Load balancing** - Ingress with SSL termination
- ✅ **Monitoring** - Prometheus and Grafana dashboards
- ✅ **Security** - Secrets management and SSL certificates
- ✅ **Scalability** - Horizontal and vertical scaling
- ✅ **Automation** - Complete deployment scripts

**ThreadStorm is ready for production use!** 🚀
