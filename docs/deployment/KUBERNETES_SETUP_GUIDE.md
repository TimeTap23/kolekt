# Kolekt Kubernetes Environment Setup Guide

## 🎯 **Complete Kubernetes Environment Setup**

This guide covers setting up a complete Kubernetes environment for Kolekt deployment, including local development and production cloud options.

## 📋 **Prerequisites**

### **Required Tools**
- **Docker Desktop** - Container runtime
- **kubectl** - Kubernetes command-line tool
- **Git** - Version control
- **OpenSSL** - For SSL certificate generation (optional)

### **System Requirements**
- **CPU**: 4+ cores
- **RAM**: 8GB+ 
- **Storage**: 50GB+ available space
- **OS**: macOS, Linux, or Windows

## 🚀 **Option 1: Local Development Setup**

### **1.1 Docker Desktop with Kubernetes**

#### **Install Docker Desktop**
```bash
# macOS
brew install --cask docker

# Windows
# Download from https://www.docker.com/products/docker-desktop

# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

#### **Enable Kubernetes in Docker Desktop**
1. Open Docker Desktop
2. Go to Settings → Kubernetes
3. Check "Enable Kubernetes"
4. Click "Apply & Restart"

#### **Verify Installation**
```bash
# Check Docker
docker --version

# Check kubectl
kubectl version --client

# Check cluster
kubectl cluster-info
```

### **1.2 Minikube Setup (Alternative)**

#### **Install Minikube**
```bash
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Windows
# Download from https://minikube.sigs.k8s.io/docs/start/
```

#### **Start Minikube**
```bash
# Start with more resources
minikube start --cpus=4 --memory=8192 --disk-size=50g

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Verify
kubectl get nodes
```

### **1.3 Kind Setup (Alternative)**

#### **Install Kind**
```bash
# macOS
brew install kind

# Linux
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Windows
# Download from https://kind.sigs.k8s.io/docs/user/quick-start/
```

#### **Create Kind Cluster**
```bash
# Create cluster configuration
cat > kind-config.yaml << EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
  - containerPort: 443
    hostPort: 443
- role: worker
- role: worker
EOF

# Create cluster
kind create cluster --name kolekt --config kind-config.yaml

# Verify
kubectl get nodes
```

## ☁️ **Option 2: Cloud Production Setup**

### **2.1 AWS EKS Setup**

#### **Install AWS CLI and eksctl**
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Configure AWS
aws configure
```

#### **Create EKS Cluster**
```bash
# Create cluster
eksctl create cluster \
  --name kolekt-cluster \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 5 \
  --managed

# Update kubeconfig
aws eks update-kubeconfig --name kolekt-cluster --region us-west-2
```

### **2.2 Google GKE Setup**

#### **Install Google Cloud SDK**
```bash
# Install gcloud
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize
gcloud init
```

#### **Create GKE Cluster**
```bash
# Create cluster
gcloud container clusters create kolekt-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-medium \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5

# Get credentials
gcloud container clusters get-credentials kolekt-cluster --zone us-central1-a
```

### **2.3 Azure AKS Setup**

#### **Install Azure CLI**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login
```

#### **Create AKS Cluster**
```bash
# Create resource group
az group create --name kolekt-rg --location eastus

# Create cluster
az aks create \
  --resource-group kolekt-rg \
  --name kolekt-cluster \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group kolekt-rg --name kolekt-cluster
```

## 🔧 **Option 3: Railway Kubernetes**

### **Install railway**
```bash
# macOS
brew install railway

# Linux
snap install railway

# Windows
# Download from https://github.com/digitalocean/railway/releases
```

### **Create DOKS Cluster**
```bash
# Authenticate
railway auth init

# Create cluster
railway kubernetes cluster create kolekt-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 3

# Save kubeconfig
railway kubernetes cluster kubeconfig save kolekt-cluster
```

## 🛠️ **Required Kubernetes Components**

### **3.1 Install NGINX Ingress Controller**

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Wait for installation
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### **3.2 Install cert-manager (for SSL)**

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for installation
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
```

### **3.3 Install Metrics Server**

```bash
# Install metrics server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Patch for self-signed certificates (if needed)
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

## 🔐 **SSL Certificate Setup**

### **Option A: Let's Encrypt (Production)**

```bash
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

### **Option B: Self-Signed (Development)**

```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout tls.key -out tls.crt \
    -subj "/CN=kolekt.local"

# Create TLS secret (will be used in deployment)
kubectl create secret tls kolekt-tls \
    --key tls.key --cert tls.crt \
    --dry-run=client -o yaml > k8s/tls-secret.yaml
```

## 📊 **Monitoring Stack Setup**

### **Install Prometheus Operator (Optional)**

```bash
# Add Prometheus Operator Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus Operator
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.enabled=true \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
```

## 🔧 **Environment Configuration**

### **4.1 Create Production Environment**

```bash
# Copy environment template
cp env.production .env.production

# Edit with your values
nano .env.production
```

### **4.2 Encode Secrets**

```bash
# Run secrets encoder
./k8s/encode-secrets.sh

# Copy encoded values to secrets file
# Edit k8s/secrets.yaml with the encoded values
```

### **4.3 Update Docker Image**

```bash
# Build and push Docker image
docker build -t ghcr.io/your-username/kolekt:latest .
docker push ghcr.io/your-username/kolekt:latest

# Update image in deployment
# Edit k8s/deployment.yaml to use your image
```

## 🚀 **Deployment Steps**

### **5.1 Complete Deployment**

```bash
# Deploy everything
./k8s/deploy.sh deploy
```

### **5.2 Step-by-Step Deployment**

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create secrets
kubectl apply -f k8s/secrets.yaml

# 3. Deploy Redis
kubectl apply -f k8s/redis.yaml

# 4. Deploy Kolekt
kubectl apply -f k8s/deployment.yaml

# 5. Deploy monitoring (optional)
kubectl apply -f k8s/monitoring.yaml

# 6. Create TLS secret (if using self-signed)
kubectl apply -f k8s/tls-secret.yaml
```

## 🔍 **Verification Steps**

### **6.1 Check Cluster Status**

```bash
# Check nodes
kubectl get nodes

# Check all resources
kubectl get all --all-namespaces

# Check ingress controller
kubectl get pods -n ingress-nginx
```

### **6.2 Check Kolekt Deployment**

```bash
# Check namespace
kubectl get all -n kolekt

# Check pods
kubectl get pods -n kolekt

# Check services
kubectl get services -n kolekt

# Check ingress
kubectl get ingress -n kolekt
```

### **6.3 Test Application**

```bash
# Port forward for local access
kubectl port-forward service/kolekt-service 8000:80 -n kolekt

# Test health endpoint
curl http://localhost:8000/health

# Test main application
curl http://localhost:8000/
```

## 🌐 **Access Configuration**

### **7.1 Get External IP**

```bash
# Get LoadBalancer IP
kubectl get service kolekt-service -n kolekt

# Get Ingress IP
kubectl get ingress kolekt-ingress -n kolekt
```

### **7.2 Configure DNS (Production)**

```bash
# Point your domain to the LoadBalancer IP
# Example DNS records:
# A     kolekt.com     → <load-balancer-ip>
# A     www.kolekt.com → <load-balancer-ip>
```

### **7.3 Local Development Access**

```bash
# For minikube
minikube service kolekt-service -n kolekt

# For kind
kubectl port-forward service/kolekt-service 8000:80 -n kolekt

# For cloud clusters
# Use LoadBalancer IP or Ingress URL
```

## 🔧 **Troubleshooting**

### **8.1 Common Issues**

#### **Cluster Not Ready**
```bash
# Check cluster status
kubectl cluster-info

# Check nodes
kubectl get nodes

# Check system pods
kubectl get pods -n kube-system
```

#### **Pods Not Starting**
```bash
# Check pod status
kubectl get pods -n kolekt

# Check pod events
kubectl describe pod <pod-name> -n kolekt

# Check pod logs
kubectl logs <pod-name> -n kolekt
```

#### **Services Not Accessible**
```bash
# Check service status
kubectl get services -n kolekt

# Check endpoints
kubectl get endpoints -n kolekt

# Test service connectivity
kubectl run test-pod --image=busybox -it --rm --restart=Never -- nslookup kolekt-service
```

#### **Ingress Issues**
```bash
# Check ingress status
kubectl get ingress -n kolekt

# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

### **8.2 Debug Commands**

```bash
# Get all resources
kubectl get all -n kolekt

# Check events
kubectl get events -n kolekt --sort-by='.lastTimestamp'

# Check resource usage
kubectl top pods -n kolekt

# Check HPA status
kubectl get hpa -n kolekt
```

## 📊 **Monitoring Access**

### **9.1 Prometheus**

```bash
# Port forward Prometheus
kubectl port-forward service/prometheus-service 9090:9090 -n kolekt

# Access: http://localhost:9090
```

### **9.2 Grafana**

```bash
# Port forward Grafana
kubectl port-forward service/grafana-service 3000:3000 -n kolekt

# Access: http://localhost:3000
# Username: admin
# Password: Set in secrets (grafana-password)
```

## 🎯 **Production Checklist**

### **Before Going Live**
- [ ] **Cluster created** and nodes ready
- [ ] **NGINX Ingress** controller installed
- [ ] **cert-manager** installed (for SSL)
- [ ] **Metrics server** installed
- [ ] **Environment configured** with production values
- [ ] **Secrets encoded** and applied
- [ ] **Docker image** built and pushed
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
- [ ] **Security verified** - No vulnerabilities detected

## 🚀 **Quick Start Commands**

### **Complete Setup (Local)**
```bash
# 1. Install Docker Desktop and enable Kubernetes
# 2. Install kubectl
# 3. Clone repository
git clone https://github.com/your-username/kolekt.git
cd kolekt

# 4. Configure environment
cp env.production .env.production
# Edit .env.production with your values

# 5. Encode secrets
./k8s/encode-secrets.sh

# 6. Deploy
./k8s/deploy.sh deploy

# 7. Access application
kubectl port-forward service/kolekt-service 8000:80 -n kolekt
```

### **Complete Setup (Cloud)**
```bash
# 1. Create cloud cluster (EKS/GKE/AKS)
# 2. Install kubectl and configure access
# 3. Clone repository
git clone https://github.com/your-username/kolekt.git
cd kolekt

# 4. Configure environment
cp env.production .env.production
# Edit .env.production with your values

# 5. Encode secrets
./k8s/encode-secrets.sh

# 6. Build and push image
docker build -t ghcr.io/your-username/kolekt:latest .
docker push ghcr.io/your-username/kolekt:latest

# 7. Deploy
./k8s/deploy.sh deploy

# 8. Access via LoadBalancer IP or domain
```

---

## 🎉 **Kubernetes Environment Setup Complete!**

Your Kubernetes environment is now ready for Kolekt deployment with:
- ✅ **Complete cluster setup** (local or cloud)
- ✅ **Required components** (Ingress, cert-manager, metrics)
- ✅ **SSL configuration** (Let's Encrypt or self-signed)
- ✅ **Monitoring stack** (Prometheus + Grafana)
- ✅ **Deployment automation** (scripts and guides)
- ✅ **Troubleshooting** (debug commands and solutions)

**Kolekt is ready for Kubernetes deployment!** 🚀
