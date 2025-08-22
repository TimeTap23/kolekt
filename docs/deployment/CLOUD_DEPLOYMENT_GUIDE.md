# ThreadStorm Cloud Deployment Guide

## ☁️ **Complete Cloud Deployment for ThreadStorm**

This guide provides step-by-step instructions for deploying ThreadStorm to major cloud providers with production-ready configurations.

## 🎯 **Cloud Provider Options**

### **1. AWS EKS (Elastic Kubernetes Service)**
- **Best for**: Enterprise workloads, AWS ecosystem integration
- **Pros**: Managed control plane, auto-scaling, integrated services
- **Cons**: Higher cost, complex networking

### **2. Google GKE (Google Kubernetes Engine)**
- **Best for**: Container-native applications, Google Cloud integration
- **Pros**: Excellent performance, integrated monitoring, cost-effective
- **Cons**: Google Cloud lock-in

### **3. Azure AKS (Azure Kubernetes Service)**
- **Best for**: Microsoft ecosystem, enterprise compliance
- **Pros**: Windows containers, enterprise features, compliance
- **Cons**: Limited regions, Microsoft ecosystem dependency

### **4. DigitalOcean Kubernetes**
- **Best for**: Simple deployments, cost-effective, developer-friendly
- **Pros**: Simple pricing, easy setup, good performance
- **Cons**: Limited advanced features, smaller ecosystem

## 🚀 **AWS EKS Deployment**

### **Prerequisites**
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### **AWS Configuration**
```bash
# Configure AWS credentials
aws configure

# Set your AWS region
export AWS_REGION=us-west-2
```

### **Create EKS Cluster**
```bash
# Create cluster with managed node groups
eksctl create cluster \
  --name threadstorm-cluster \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 5 \
  --managed \
  --with-oidc \
  --ssh-access \
  --ssh-public-key my-key \
  --full-ecr-access

# Update kubeconfig
aws eks update-kubeconfig --name threadstorm-cluster --region us-west-2
```

### **Deploy ThreadStorm to EKS**
```bash
# Install required components
./setup-kubernetes.sh components

# Configure environment
cp env.production .env.production
nano .env.production

# Encode secrets
./k8s/encode-secrets.sh

# Build and push Docker image
docker build -t your-aws-account.dkr.ecr.us-west-2.amazonaws.com/threadstorm:latest .
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin your-aws-account.dkr.ecr.us-west-2.amazonaws.com
docker push your-aws-account.dkr.ecr.us-west-2.amazonaws.com/threadstorm:latest

# Update image in deployment
sed -i 's|ghcr.io/your-username/threadstorm:latest|your-aws-account.dkr.ecr.us-west-2.amazonaws.com/threadstorm:latest|g' k8s/deployment.yaml

# Deploy ThreadStorm
./k8s/deploy.sh deploy
```

## 🌐 **Google GKE Deployment**

### **Prerequisites**
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install kubectl
gcloud components install kubectl

# Initialize gcloud
gcloud init
```

### **Create GKE Cluster**
```bash
# Set project
gcloud config set project your-project-id

# Create cluster
gcloud container clusters create threadstorm-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type e2-medium \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 5 \
  --enable-autorepair \
  --enable-autoupgrade \
  --enable-network-policy

# Get credentials
gcloud container clusters get-credentials threadstorm-cluster --zone us-central1-a
```

### **Deploy ThreadStorm to GKE**
```bash
# Install required components
./setup-kubernetes.sh components

# Configure environment
cp env.production .env.production
nano .env.production

# Encode secrets
./k8s/encode-secrets.sh

# Build and push Docker image
docker build -t gcr.io/your-project-id/threadstorm:latest .
gcloud auth configure-docker
docker push gcr.io/your-project-id/threadstorm:latest

# Update image in deployment
sed -i 's|ghcr.io/your-username/threadstorm:latest|gcr.io/your-project-id/threadstorm:latest|g' k8s/deployment.yaml

# Deploy ThreadStorm
./k8s/deploy.sh deploy
```

## 🔵 **Azure AKS Deployment**

### **Prerequisites**
```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Install kubectl
az aks install-cli

# Login to Azure
az login
```

### **Create AKS Cluster**
```bash
# Set subscription
az account set --subscription your-subscription-id

# Create resource group
az group create --name threadstorm-rg --location eastus

# Create cluster
az aks create \
  --resource-group threadstorm-rg \
  --name threadstorm-cluster \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 5

# Get credentials
az aks get-credentials --resource-group threadstorm-rg --name threadstorm-cluster
```

### **Deploy ThreadStorm to AKS**
```bash
# Install required components
./setup-kubernetes.sh components

# Configure environment
cp env.production .env.production
nano .env.production

# Encode secrets
./k8s/encode-secrets.sh

# Build and push Docker image
docker build -t your-registry.azurecr.io/threadstorm:latest .
az acr login --name your-registry
docker push your-registry.azurecr.io/threadstorm:latest

# Update image in deployment
sed -i 's|ghcr.io/your-username/threadstorm:latest|your-registry.azurecr.io/threadstorm:latest|g' k8s/deployment.yaml

# Deploy ThreadStorm
./k8s/deploy.sh deploy
```

## 🐳 **DigitalOcean Kubernetes Deployment**

### **Prerequisites**
```bash
# Install doctl
# macOS
brew install doctl

# Linux
snap install doctl

# Windows
# Download from https://github.com/digitalocean/doctl/releases

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### **Create DOKS Cluster**
```bash
# Authenticate
doctl auth init

# Create cluster
doctl kubernetes cluster create threadstorm-cluster \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 3 \
  --version 1.24.4-do.0

# Save kubeconfig
doctl kubernetes cluster kubeconfig save threadstorm-cluster
```

### **Deploy ThreadStorm to DOKS**
```bash
# Install required components
./setup-kubernetes.sh components

# Configure environment
cp env.production .env.production
nano .env.production

# Encode secrets
./k8s/encode-secrets.sh

# Build and push Docker image
docker build -t registry.digitalocean.com/your-registry/threadstorm:latest .
doctl registry login
docker push registry.digitalocean.com/your-registry/threadstorm:latest

# Update image in deployment
sed -i 's|ghcr.io/your-username/threadstorm:latest|registry.digitalocean.com/your-registry/threadstorm:latest|g' k8s/deployment.yaml

# Deploy ThreadStorm
./k8s/deploy.sh deploy
```

## 🔧 **Cloud-Specific Configuration**

### **AWS EKS Configuration**
```yaml
# Update k8s/deployment.yaml for EKS
apiVersion: apps/v1
kind: Deployment
metadata:
  name: threadstorm
  namespace: threadstorm
spec:
  template:
    spec:
      containers:
      - name: threadstorm
        image: your-aws-account.dkr.ecr.us-west-2.amazonaws.com/threadstorm:latest
        env:
        - name: AWS_REGION
          value: "us-west-2"
        - name: ENABLE_KMS_ENCRYPTION
          value: "true"
```

### **Google GKE Configuration**
```yaml
# Update k8s/deployment.yaml for GKE
apiVersion: apps/v1
kind: Deployment
metadata:
  name: threadstorm
  namespace: threadstorm
spec:
  template:
    spec:
      containers:
      - name: threadstorm
        image: gcr.io/your-project-id/threadstorm:latest
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "your-project-id"
```

### **Azure AKS Configuration**
```yaml
# Update k8s/deployment.yaml for AKS
apiVersion: apps/v1
kind: Deployment
metadata:
  name: threadstorm
  namespace: threadstorm
spec:
  template:
    spec:
      containers:
      - name: threadstorm
        image: your-registry.azurecr.io/threadstorm:latest
        env:
        - name: AZURE_SUBSCRIPTION_ID
          value: "your-subscription-id"
```

## 🔐 **Cloud-Specific Security**

### **AWS EKS Security**
```bash
# Create IAM roles for service accounts
eksctl create iamserviceaccount \
  --name threadstorm-sa \
  --namespace threadstorm \
  --cluster threadstorm-cluster \
  --attach-policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess \
  --approve

# Enable pod identity
eksctl create iamserviceaccount \
  --name threadstorm-pod-identity \
  --namespace threadstorm \
  --cluster threadstorm-cluster \
  --role-name threadstorm-pod-role \
  --attach-policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess \
  --approve
```

### **Google GKE Security**
```bash
# Enable workload identity
gcloud container clusters update threadstorm-cluster \
  --zone us-central1-a \
  --workload-pool=your-project-id.svc.id.goog

# Create service account
gcloud iam service-accounts create threadstorm-sa \
  --display-name="ThreadStorm Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:threadstorm-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

### **Azure AKS Security**
```bash
# Enable managed identity
az aks update \
  --resource-group threadstorm-rg \
  --name threadstorm-cluster \
  --enable-managed-identity

# Create user-assigned managed identity
az identity create \
  --resource-group threadstorm-rg \
  --name threadstorm-identity

# Assign permissions
az role assignment create \
  --assignee "your-identity-client-id" \
  --role "Storage Blob Data Reader" \
  --scope "/subscriptions/your-subscription-id/resourceGroups/threadstorm-rg"
```

## 📊 **Cloud Monitoring Integration**

### **AWS CloudWatch**
```yaml
# Add CloudWatch agent to k8s/deployment.yaml
- name: cloudwatch-agent
  image: amazon/cloudwatch-agent:latest
  env:
  - name: AWS_REGION
    value: "us-west-2"
  volumeMounts:
  - name: cwagentconfig
    mountPath: /etc/cwagentconfig
volumes:
- name: cwagentconfig
  configMap:
    name: cwagentconfig
```

### **Google Cloud Monitoring**
```yaml
# Add Cloud Monitoring to k8s/deployment.yaml
- name: cloud-monitoring
  image: gcr.io/stackdriver-agents/stackdriver-logging-agent:latest
  env:
  - name: GOOGLE_CLOUD_PROJECT
    value: "your-project-id"
```

### **Azure Monitor**
```yaml
# Add Azure Monitor to k8s/deployment.yaml
- name: azure-monitor
  image: mcr.microsoft.com/azuremonitor/containerinsights/ciprod:ciprod11012020
  env:
  - name: AZURE_SUBSCRIPTION_ID
    value: "your-subscription-id"
```

## 🌐 **Domain and SSL Configuration**

### **AWS Route 53 + ACM**
```bash
# Create hosted zone
aws route53 create-hosted-zone \
  --name threadstorm.com \
  --caller-reference $(date +%s)

# Request SSL certificate
aws acm request-certificate \
  --domain-name threadstorm.com \
  --subject-alternative-names www.threadstorm.com \
  --validation-method DNS

# Update DNS records
aws route53 change-resource-record-sets \
  --hosted-zone-id your-hosted-zone-id \
  --change-batch file://dns-changes.json
```

### **Google Cloud DNS + Certificate Manager**
```bash
# Create managed zone
gcloud dns managed-zones create threadstorm-zone \
  --dns-name="threadstorm.com." \
  --description="ThreadStorm DNS zone"

# Create SSL certificate
gcloud compute ssl-certificates create threadstorm-cert \
  --domains=threadstorm.com,www.threadstorm.com \
  --global
```

### **Azure DNS + Key Vault**
```bash
# Create DNS zone
az network dns zone create \
  --resource-group threadstorm-rg \
  --name threadstorm.com

# Create SSL certificate in Key Vault
az keyvault certificate create \
  --vault-name threadstorm-vault \
  --name threadstorm-cert \
  --policy '{"x509CertificateProperties":{"subject":"CN=threadstorm.com"},"issuerParameters":{"name":"Self"}}'
```

## 🔄 **CI/CD Pipeline Setup**

### **GitHub Actions for AWS EKS**
```yaml
# .github/workflows/deploy-eks.yml
name: Deploy to EKS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    - name: Build and push Docker image
      run: |
        docker build -t ${{ secrets.ECR_REGISTRY }}/threadstorm:${{ github.sha }} .
        docker push ${{ secrets.ECR_REGISTRY }}/threadstorm:${{ github.sha }}
    - name: Deploy to EKS
      run: |
        aws eks update-kubeconfig --name threadstorm-cluster --region us-west-2
        kubectl set image deployment/threadstorm threadstorm=${{ secrets.ECR_REGISTRY }}/threadstorm:${{ github.sha }} -n threadstorm
```

### **GitHub Actions for Google GKE**
```yaml
# .github/workflows/deploy-gke.yml
name: Deploy to GKE
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Google Cloud
      uses: google-github-actions/setup-gcloud@v0
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
    - name: Build and push Docker image
      run: |
        docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/threadstorm:${{ github.sha }} .
        docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/threadstorm:${{ github.sha }}
    - name: Deploy to GKE
      run: |
        gcloud container clusters get-credentials threadstorm-cluster --zone us-central1-a
        kubectl set image deployment/threadstorm threadstorm=gcr.io/${{ secrets.GCP_PROJECT_ID }}/threadstorm:${{ github.sha }} -n threadstorm
```

## 📈 **Scaling and Performance**

### **Auto-scaling Configuration**
```yaml
# Update HPA for cloud environments
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: threadstorm-hpa
  namespace: threadstorm
spec:
  minReplicas: 3
  maxReplicas: 20  # Higher for cloud
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60  # Lower threshold for cloud
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
```

### **Resource Optimization**
```yaml
# Optimize resource requests for cloud
resources:
  requests:
    memory: "512Mi"  # Higher for cloud
    cpu: "500m"      # Higher for cloud
  limits:
    memory: "1Gi"    # Higher for cloud
    cpu: "1000m"     # Higher for cloud
```

## 🔍 **Monitoring and Alerting**

### **Cloud-native Monitoring**
```bash
# AWS CloudWatch Alarms
aws cloudwatch put-metric-alarm \
  --alarm-name threadstorm-cpu-high \
  --alarm-description "CPU utilization is high" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold

# Google Cloud Monitoring Alerts
gcloud alpha monitoring policies create \
  --policy-from-file=alerting-policy.yaml

# Azure Monitor Alerts
az monitor metrics alert create \
  --name "threadstorm-cpu-alert" \
  --resource-group threadstorm-rg \
  --scopes /subscriptions/your-subscription-id/resourceGroups/threadstorm-rg/providers/Microsoft.ContainerService/managedClusters/threadstorm-cluster \
  --condition "avg Percentage CPU > 80" \
  --description "CPU utilization is high"
```

## 🎯 **Production Checklist**

### **Pre-Deployment**
- [ ] **Cloud account** configured and billing set up
- [ ] **Kubernetes cluster** created and accessible
- [ ] **Container registry** configured
- [ ] **Environment variables** configured for cloud
- [ ] **Secrets encoded** and applied
- [ ] **SSL certificates** configured
- [ ] **Domain DNS** pointing to cloud load balancer
- [ ] **Monitoring** stack deployed
- [ ] **Backup strategy** implemented
- [ ] **CI/CD pipeline** configured

### **Post-Deployment**
- [ ] **All pods running** - Health checks passing
- [ ] **Services accessible** - Load balancer working
- [ ] **Ingress functional** - SSL certificates valid
- [ ] **Monitoring active** - Metrics being collected
- [ ] **Auto-scaling working** - HPA responding to load
- [ ] **Performance acceptable** - Response times < 200ms
- [ ] **Security verified** - No vulnerabilities detected
- [ ] **Backup tested** - Data protection working

## 🚀 **Quick Cloud Deployment Commands**

### **AWS EKS (Complete)**
```bash
# 1. Create cluster
eksctl create cluster --name threadstorm-cluster --region us-west-2 --node-type t3.medium --nodes 3

# 2. Setup environment
./setup-kubernetes.sh components
cp env.production .env.production
nano .env.production

# 3. Deploy
./k8s/encode-secrets.sh
docker build -t your-account.dkr.ecr.us-west-2.amazonaws.com/threadstorm:latest .
docker push your-account.dkr.ecr.us-west-2.amazonaws.com/threadstorm:latest
./k8s/deploy.sh deploy
```

### **Google GKE (Complete)**
```bash
# 1. Create cluster
gcloud container clusters create threadstorm-cluster --zone us-central1-a --num-nodes 3

# 2. Setup environment
./setup-kubernetes.sh components
cp env.production .env.production
nano .env.production

# 3. Deploy
./k8s/encode-secrets.sh
docker build -t gcr.io/your-project/threadstorm:latest .
docker push gcr.io/your-project/threadstorm:latest
./k8s/deploy.sh deploy
```

---

## 🎉 **ThreadStorm Cloud Deployment Complete!**

Your ThreadStorm application is now ready for cloud deployment with:
- ✅ **Multi-cloud support** - AWS, Google, Azure, DigitalOcean
- ✅ **Production-ready configurations** - Auto-scaling, monitoring, security
- ✅ **CI/CD integration** - Automated deployments
- ✅ **Cloud-native features** - Managed services, monitoring, alerting
- ✅ **Cost optimization** - Resource management and scaling
- ✅ **Security hardening** - Cloud-specific security features

**ThreadStorm is ready for production cloud deployment!** 🚀
