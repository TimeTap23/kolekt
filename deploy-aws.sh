#!/bin/bash

# Kolekt AWS EKS Deployment Script
# This script automates the complete AWS EKS deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="kolekt-cluster"
REGION="us-west-2"
NODE_TYPE="t3.medium"
NODE_COUNT=3
MIN_NODES=1
MAX_NODES=5

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking AWS EKS prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed"
        print_info "Please install AWS CLI first: https://aws.amazon.com/cli/"
        exit 1
    fi
    
    # Check eksctl
    if ! command -v eksctl &> /dev/null; then
        print_error "eksctl is not installed"
        print_info "Please install eksctl first: https://eksctl.io/"
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        print_info "Please install kubectl first: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        print_info "Please install Docker first: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured"
        print_info "Please run: aws configure"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Create EKS cluster
create_cluster() {
    print_info "Creating EKS cluster..."
    
    # Check if cluster already exists
    if eksctl get cluster --name $CLUSTER_NAME --region $REGION &> /dev/null; then
        print_warning "Cluster $CLUSTER_NAME already exists"
        read -p "Do you want to use the existing cluster? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Please delete the existing cluster or use a different name"
            exit 1
        fi
    else
        # Create cluster
        eksctl create cluster \
            --name $CLUSTER_NAME \
            --region $REGION \
            --nodegroup-name standard-workers \
            --node-type $NODE_TYPE \
            --nodes $NODE_COUNT \
            --nodes-min $MIN_NODES \
            --nodes-max $MAX_NODES \
            --managed \
            --with-oidc \
            --ssh-access \
            --full-ecr-access
        
        print_status "EKS cluster created successfully"
    fi
    
    # Update kubeconfig
    aws eks update-kubeconfig --name $CLUSTER_NAME --region $REGION
    print_status "Kubeconfig updated"
}

# Setup ECR repository
setup_ecr() {
    print_info "Setting up ECR repository..."
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_REGISTRY="$AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"
    ECR_REPOSITORY="$ECR_REGISTRY/kolekt"
    
    # Create ECR repository if it doesn't exist
    if ! aws ecr describe-repositories --repository-names kolekt --region $REGION &> /dev/null; then
        aws ecr create-repository --repository-name kolekt --region $REGION
        print_status "ECR repository created"
    else
        print_status "ECR repository already exists"
    fi
    
    # Login to ECR
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REGISTRY
    print_status "Logged in to ECR"
    
    # Export for use in other functions
    export ECR_REPOSITORY
}

# Build and push Docker image
build_and_push_image() {
    print_info "Building and pushing Docker image..."
    
    # Build image
    docker build -t $ECR_REPOSITORY:latest .
    print_status "Docker image built"
    
    # Push image
    docker push $ECR_REPOSITORY:latest
    print_status "Docker image pushed to ECR"
}

# Update deployment configuration
update_deployment() {
    print_info "Updating deployment configuration..."
    
    # Update image in deployment file
    sed -i.bak "s|ghcr.io/your-username/kolekt:latest|$ECR_REPOSITORY:latest|g" k8s/deployment.yaml
    
    # Add AWS-specific environment variables
    cat >> k8s/deployment.yaml << EOF
        - name: AWS_REGION
          value: "$REGION"
        - name: ENABLE_KMS_ENCRYPTION
          value: "true"
EOF
    
    print_status "Deployment configuration updated"
}

# Install Kubernetes components
install_components() {
    print_info "Installing Kubernetes components..."
    
    # Install NGINX Ingress Controller
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
    
    # Wait for ingress controller
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=120s
    
    # Install cert-manager
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
    
    # Wait for cert-manager
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
    
    # Install metrics server
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    
    print_status "Kubernetes components installed"
}

# Deploy Kolekt
deploy_kolekt() {
    print_info "Deploying Kolekt to EKS..."
    
    # Create namespace
    kubectl apply -f k8s/namespace.yaml
    
    # Create secrets
    kubectl apply -f k8s/secrets.yaml
    
    # Deploy Redis
    kubectl apply -f k8s/redis.yaml
    
    # Deploy Kolekt
    kubectl apply -f k8s/deployment.yaml
    
    # Deploy monitoring (optional)
    kubectl apply -f k8s/monitoring.yaml
    
    print_status "Kolekt deployed to EKS"
}

# Wait for deployment
wait_for_deployment() {
    print_info "Waiting for deployment to be ready..."
    
    # Wait for Kolekt deployment
    kubectl wait --for=condition=available deployment/kolekt -n kolekt --timeout=600s
    
    # Wait for Redis deployment
    kubectl wait --for=condition=ready pod -l app=kolekt-redis -n kolekt --timeout=300s
    
    print_status "Deployment is ready"
}

# Get service information
get_service_info() {
    print_info "Getting service information..."
    
    # Get LoadBalancer IP
    LOAD_BALANCER_IP=$(kubectl get service kolekt-service -n kolekt -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -n "$LOAD_BALANCER_IP" ]; then
        echo ""
        echo "🎉 Kolekt is now accessible at:"
        echo "   Main Application: http://$LOAD_BALANCER_IP"
        echo "   Admin Panel: http://$LOAD_BALANCER_IP/admin"
        echo "   Health Check: http://$LOAD_BALANCER_IP/health"
        echo ""
        echo "📊 Monitoring:"
        echo "   Prometheus: http://$LOAD_BALANCER_IP:9090"
        echo "   Grafana: http://$LOAD_BALANCER_IP:3000"
        echo ""
    else
        print_warning "LoadBalancer IP not available yet"
        print_info "You may need to wait a few minutes for the LoadBalancer to be provisioned"
    fi
}

# Show cluster information
show_cluster_info() {
    print_info "Cluster Information:"
    echo ""
    echo "Cluster Name: $CLUSTER_NAME"
    echo "Region: $REGION"
    echo "Node Type: $NODE_TYPE"
    echo "Node Count: $NODE_COUNT"
    echo "Auto-scaling: $MIN_NODES - $MAX_NODES nodes"
    echo ""
    echo "Useful Commands:"
    echo "  - Check cluster status: eksctl get cluster --name $CLUSTER_NAME --region $REGION"
    echo "  - View pods: kubectl get pods -n kolekt"
    echo "  - View logs: kubectl logs -f deployment/kolekt -n kolekt"
    echo "  - Scale deployment: kubectl scale deployment kolekt --replicas=5 -n kolekt"
    echo "  - Delete cluster: eksctl delete cluster --name $CLUSTER_NAME --region $REGION"
}

# Main deployment function
main() {
    echo -e "${BLUE}☁️  Kolekt AWS EKS Deployment${NC}"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    create_cluster
    setup_ecr
    build_and_push_image
    update_deployment
    install_components
    deploy_kolekt
    wait_for_deployment
    get_service_info
    
    echo ""
    print_status "AWS EKS deployment completed successfully!"
    echo ""
    show_cluster_info
}

# Handle script arguments
case "${1:-}" in
    "deploy")
        main
        ;;
    "cluster")
        check_prerequisites
        create_cluster
        ;;
    "ecr")
        setup_ecr
        ;;
    "image")
        setup_ecr
        build_and_push_image
        ;;
    "deploy-app")
        install_components
        deploy_kolekt
        wait_for_deployment
        get_service_info
        ;;
    "status")
        kubectl get all -n kolekt
        ;;
    "logs")
        kubectl logs -f deployment/kolekt -n kolekt
        ;;
    "delete")
        print_warning "This will delete the entire EKS cluster!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            eksctl delete cluster --name $CLUSTER_NAME --region $REGION
            print_status "Cluster deleted"
        else
            print_info "Deletion cancelled"
        fi
        ;;
    "help")
        echo "Usage: $0 {deploy|cluster|ecr|image|deploy-app|status|logs|delete|help}"
        echo ""
        echo "Commands:"
        echo "  deploy      - Complete deployment (cluster, ECR, image, app)"
        echo "  cluster     - Create EKS cluster only"
        echo "  ecr         - Setup ECR repository only"
        echo "  image       - Build and push Docker image only"
        echo "  deploy-app  - Deploy Kolekt application only"
        echo "  status      - Check deployment status"
        echo "  logs        - View application logs"
        echo "  delete      - Delete EKS cluster"
        echo "  help        - Show this help message"
        ;;
    *)
        echo "Usage: $0 {deploy|cluster|ecr|image|deploy-app|status|logs|delete|help}"
        echo ""
        echo "This script automates Kolekt deployment to AWS EKS."
        echo ""
        echo "For complete deployment: $0 deploy"
        echo "For step-by-step deployment: Use individual commands"
        exit 1
        ;;
esac
