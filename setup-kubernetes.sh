#!/bin/bash

# Kolekt Kubernetes Environment Setup Script
# This script helps set up a complete Kubernetes environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CLUSTER_TYPE=""
CLUSTER_NAME="kolekt-cluster"

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
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        print_info "Please install Docker Desktop first: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        print_info "Please install kubectl first: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Setup local cluster
setup_local_cluster() {
    print_info "Setting up local Kubernetes cluster..."
    
    # Check if Docker Desktop Kubernetes is enabled
    if kubectl cluster-info &> /dev/null; then
        print_status "Docker Desktop Kubernetes is already running"
        return
    fi
    
    print_warning "Docker Desktop Kubernetes is not enabled"
    print_info "Please enable Kubernetes in Docker Desktop:"
    print_info "1. Open Docker Desktop"
    print_info "2. Go to Settings → Kubernetes"
    print_info "3. Check 'Enable Kubernetes'"
    print_info "4. Click 'Apply & Restart'"
    print_info "5. Wait for Kubernetes to start"
    
    read -p "Press Enter when Kubernetes is enabled..."
    
    # Verify cluster is running
    if kubectl cluster-info &> /dev/null; then
        print_status "Kubernetes cluster is now running"
    else
        print_error "Kubernetes cluster is not accessible"
        exit 1
    fi
}

# Install required components
install_components() {
    print_info "Installing required Kubernetes components..."
    
    # Install NGINX Ingress Controller
    print_info "Installing NGINX Ingress Controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
    
    # Wait for ingress controller
    print_info "Waiting for NGINX Ingress Controller..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=120s
    
    # Install cert-manager
    print_info "Installing cert-manager..."
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
    
    # Wait for cert-manager
    print_info "Waiting for cert-manager..."
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
    
    # Install metrics server
    print_info "Installing metrics server..."
    kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
    
    # Patch metrics server for self-signed certificates (if needed)
    kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]' 2>/dev/null || true
    
    print_status "All components installed successfully"
}

# Create SSL certificate
setup_ssl() {
    print_info "Setting up SSL certificates..."
    
    # Create self-signed certificate for development
    if [ ! -f "tls.key" ] || [ ! -f "tls.crt" ]; then
        print_info "Generating self-signed SSL certificate..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout tls.key -out tls.crt \
            -subj "/CN=kolekt.local"
    fi
    
    # Create TLS secret
    print_info "Creating TLS secret..."
    kubectl create secret tls kolekt-tls \
        --key tls.key --cert tls.crt \
        --dry-run=client -o yaml > k8s/tls-secret.yaml
    
    print_status "SSL certificates configured"
}

# Configure environment
configure_environment() {
    print_info "Configuring environment..."
    
    # Check if .env.production exists
    if [ ! -f ".env.production" ]; then
        print_info "Creating production environment file..."
        cp env.production .env.production
        print_warning "Please edit .env.production with your actual values"
        print_info "Then run: ./k8s/encode-secrets.sh"
    else
        print_status "Production environment file already exists"
    fi
}

# Verify setup
verify_setup() {
    print_info "Verifying Kubernetes setup..."
    
    echo ""
    echo "Cluster Information:"
    kubectl cluster-info
    
    echo ""
    echo "Nodes:"
    kubectl get nodes
    
    echo ""
    echo "System Pods:"
    kubectl get pods -n kube-system
    
    echo ""
    echo "Ingress Controller:"
    kubectl get pods -n ingress-nginx
    
    echo ""
    echo "Cert Manager:"
    kubectl get pods -n cert-manager
    
    print_status "Kubernetes setup verification complete"
}

# Show next steps
show_next_steps() {
    print_info "Next steps for Kolekt deployment:"
    echo ""
    echo "1. Configure environment:"
    echo "   nano .env.production"
    echo ""
    echo "2. Encode secrets:"
    echo "   ./k8s/encode-secrets.sh"
    echo ""
    echo "3. Build and push Docker image:"
    echo "   docker build -t ghcr.io/your-username/kolekt:latest ."
    echo "   docker push ghcr.io/your-username/kolekt:latest"
    echo ""
    echo "4. Deploy Kolekt:"
    echo "   ./k8s/deploy.sh deploy"
    echo ""
    echo "5. Access the application:"
    echo "   kubectl port-forward service/kolekt-service 8000:80 -n kolekt"
    echo ""
    echo "6. Access monitoring:"
    echo "   kubectl port-forward service/prometheus-service 9090:9090 -n kolekt"
    echo "   kubectl port-forward service/grafana-service 3000:3000 -n kolekt"
}

# Main setup function
main() {
    echo -e "${BLUE}☸️  Kolekt Kubernetes Environment Setup${NC}"
    echo "=========================================="
    echo ""
    
    check_prerequisites
    setup_local_cluster
    install_components
    setup_ssl
    configure_environment
    verify_setup
    
    echo ""
    print_status "Kubernetes environment setup completed successfully!"
    echo ""
    show_next_steps
}

# Handle script arguments
case "${1:-}" in
    "local")
        main
        ;;
    "verify")
        verify_setup
        ;;
    "components")
        install_components
        ;;
    "ssl")
        setup_ssl
        ;;
    "help")
        echo "Usage: $0 {local|verify|components|ssl|help}"
        echo ""
        echo "Commands:"
        echo "  local      - Complete local setup (Docker Desktop Kubernetes)"
        echo "  verify     - Verify current setup"
        echo "  components - Install required components only"
        echo "  ssl        - Setup SSL certificates only"
        echo "  help       - Show this help message"
        ;;
    *)
        echo "Usage: $0 {local|verify|components|ssl|help}"
        echo ""
        echo "This script sets up a complete Kubernetes environment for Kolekt."
        echo ""
        echo "For local development: $0 local"
        echo "For cloud deployment: Follow KUBERNETES_SETUP_GUIDE.md"
        exit 1
        ;;
esac
