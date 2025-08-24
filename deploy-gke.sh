#!/bin/bash

# Kolekt Google GKE Deployment Script
# This script automates the complete Google GKE deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_NAME="kolekt-cluster"
ZONE="us-central1-a"
PROJECT_ID=""
NODE_COUNT=3
MACHINE_TYPE="e2-medium"
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
    print_info "Checking Google GKE prerequisites..."
    
    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud SDK is not installed"
        print_info "Please install Google Cloud SDK first: https://cloud.google.com/sdk/docs/install"
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
    
    # Check gcloud authentication
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_error "Google Cloud not authenticated"
        print_info "Please run: gcloud auth login"
        exit 1
    fi
    
    # Get project ID if not set
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
        if [ -z "$PROJECT_ID" ]; then
            print_error "No Google Cloud project configured"
            print_info "Please set a project: gcloud config set project YOUR_PROJECT_ID"
            exit 1
        fi
    fi
    
    print_status "Prerequisites check passed"
    print_info "Using project: $PROJECT_ID"
}

# Create GKE cluster
create_cluster() {
    print_info "Creating GKE cluster..."
    
    # Check if cluster already exists
    if gcloud container clusters describe $CLUSTER_NAME --zone $ZONE &> /dev/null; then
        print_warning "Cluster $CLUSTER_NAME already exists"
        read -p "Do you want to use the existing cluster? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Please delete the existing cluster or use a different name"
            exit 1
        fi
    else
        # Create cluster
        gcloud container clusters create $CLUSTER_NAME \
            --zone $ZONE \
            --num-nodes $NODE_COUNT \
            --machine-type $MACHINE_TYPE \
            --enable-autoscaling \
            --min-nodes $MIN_NODES \
            --max-nodes $MAX_NODES \
            --enable-autorepair \
            --enable-autoupgrade \
            --enable-network-policy \
            --enable-legacy-authorization \
            --enable-basic-auth \
            --enable-ip-alias
        
        print_status "GKE cluster created successfully"
    fi
    
    # Get credentials
    gcloud container clusters get-credentials $CLUSTER_NAME --zone $ZONE
    print_status "Kubeconfig updated"
}

# Setup Google Container Registry
setup_gcr() {
    print_info "Setting up Google Container Registry..."
    
    # Configure Docker for GCR
    gcloud auth configure-docker
    
    # Set GCR repository
    GCR_REPOSITORY="gcr.io/$PROJECT_ID/kolekt"
    export GCR_REPOSITORY
    
    print_status "GCR configured"
}

# Build and push Docker image
build_and_push_image() {
    print_info "Building and pushing Docker image..."
    
    # Build image
    docker build -t $GCR_REPOSITORY:latest .
    print_status "Docker image built"
    
    # Push image
    docker push $GCR_REPOSITORY:latest
    print_status "Docker image pushed to GCR"
}

# Update deployment configuration
update_deployment() {
    print_info "Updating deployment configuration..."
    
    # Update image in deployment file
    sed -i.bak "s|ghcr.io/your-username/kolekt:latest|$GCR_REPOSITORY:latest|g" k8s/deployment.yaml
    
    # Add Google Cloud-specific environment variables
    cat >> k8s/deployment.yaml << EOF
        - name: GOOGLE_CLOUD_PROJECT
          value: "$PROJECT_ID"
        - name: GOOGLE_CLOUD_ZONE
          value: "$ZONE"
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
    print_info "Deploying Kolekt to GKE..."
    
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
    
    print_status "Kolekt deployed to GKE"
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
    echo "Project ID: $PROJECT_ID"
    echo "Zone: $ZONE"
    echo "Machine Type: $MACHINE_TYPE"
    echo "Node Count: $NODE_COUNT"
    echo "Auto-scaling: $MIN_NODES - $MAX_NODES nodes"
    echo ""
    echo "Useful Commands:"
    echo "  - Check cluster status: gcloud container clusters describe $CLUSTER_NAME --zone $ZONE"
    echo "  - View pods: kubectl get pods -n kolekt"
    echo "  - View logs: kubectl logs -f deployment/kolekt -n kolekt"
    echo "  - Scale deployment: kubectl scale deployment kolekt --replicas=5 -n kolekt"
    echo "  - Delete cluster: gcloud container clusters delete $CLUSTER_NAME --zone $ZONE"
}

# Main deployment function
main() {
    echo -e "${BLUE}☁️  Kolekt Google GKE Deployment${NC}"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    create_cluster
    setup_gcr
    build_and_push_image
    update_deployment
    install_components
    deploy_kolekt
    wait_for_deployment
    get_service_info
    
    echo ""
    print_status "Google GKE deployment completed successfully!"
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
    "gcr")
        setup_gcr
        ;;
    "image")
        setup_gcr
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
        print_warning "This will delete the entire GKE cluster!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            gcloud container clusters delete $CLUSTER_NAME --zone $ZONE
            print_status "Cluster deleted"
        else
            print_info "Deletion cancelled"
        fi
        ;;
    "help")
        echo "Usage: $0 {deploy|cluster|gcr|image|deploy-app|status|logs|delete|help}"
        echo ""
        echo "Commands:"
        echo "  deploy      - Complete deployment (cluster, GCR, image, app)"
        echo "  cluster     - Create GKE cluster only"
        echo "  gcr         - Setup Google Container Registry only"
        echo "  image       - Build and push Docker image only"
        echo "  deploy-app  - Deploy Kolekt application only"
        echo "  status      - Check deployment status"
        echo "  logs        - View application logs"
        echo "  delete      - Delete GKE cluster"
        echo "  help        - Show this help message"
        ;;
    *)
        echo "Usage: $0 {deploy|cluster|gcr|image|deploy-app|status|logs|delete|help}"
        echo ""
        echo "This script automates Kolekt deployment to Google GKE."
        echo ""
        echo "For complete deployment: $0 deploy"
        echo "For step-by-step deployment: Use individual commands"
        exit 1
        ;;
esac
