#!/bin/bash

# ThreadStorm Kubernetes Deployment Script
# This script handles the complete Kubernetes deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="threadstorm"
DOCKER_IMAGE="ghcr.io/your-username/threadstorm:latest"

# Logging
LOG_FILE="k8s-deploy.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo -e "${BLUE}☸️  ThreadStorm Kubernetes Deployment${NC}"
echo "=========================================="
echo "Timestamp: $(date)"
echo ""

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
    print_info "Checking Kubernetes prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        exit 1
    fi
    
    # Check if kubectl can connect to cluster
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Cannot connect to Kubernetes cluster"
        print_info "Please ensure your kubeconfig is properly configured"
        exit 1
    fi
    
    # Check if namespace exists
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        print_warning "Namespace $NAMESPACE does not exist, will create it"
    fi
    
    print_status "Prerequisites check passed"
}

# Build and push Docker image
build_and_push_image() {
    print_info "Building and pushing Docker image..."
    
    # Build image
    docker build -t $DOCKER_IMAGE .
    
    # Push image
    docker push $DOCKER_IMAGE
    
    print_status "Docker image built and pushed successfully"
}

# Create namespace
create_namespace() {
    print_info "Creating namespace..."
    
    kubectl apply -f k8s/namespace.yaml
    
    print_status "Namespace created"
}

# Setup secrets
setup_secrets() {
    print_info "Setting up secrets..."
    
    # Check if secrets file exists
    if [ ! -f "k8s/secrets.yaml" ]; then
        print_error "k8s/secrets.yaml not found"
        print_info "Please run: ./k8s/encode-secrets.sh"
        exit 1
    fi
    
    # Apply secrets
    kubectl apply -f k8s/secrets.yaml
    
    print_status "Secrets configured"
}

# Deploy Redis
deploy_redis() {
    print_info "Deploying Redis..."
    
    kubectl apply -f k8s/redis.yaml
    
    # Wait for Redis to be ready
    print_info "Waiting for Redis to be ready..."
    kubectl wait --for=condition=ready pod -l app=threadstorm-redis -n $NAMESPACE --timeout=300s
    
    print_status "Redis deployed successfully"
}

# Deploy ThreadStorm
deploy_threadstorm() {
    print_info "Deploying ThreadStorm application..."
    
    kubectl apply -f k8s/deployment.yaml
    
    # Wait for deployment to be ready
    print_info "Waiting for ThreadStorm deployment to be ready..."
    kubectl wait --for=condition=available deployment/threadstorm -n $NAMESPACE --timeout=600s
    
    print_status "ThreadStorm deployed successfully"
}

# Check deployment status
check_deployment() {
    print_info "Checking deployment status..."
    
    echo ""
    echo "Pod Status:"
    kubectl get pods -n $NAMESPACE
    
    echo ""
    echo "Service Status:"
    kubectl get services -n $NAMESPACE
    
    echo ""
    echo "Ingress Status:"
    kubectl get ingress -n $NAMESPACE
    
    echo ""
    echo "HPA Status:"
    kubectl get hpa -n $NAMESPACE
}

# Health check
health_check() {
    print_info "Performing health check..."
    
    # Get the service URL
    SERVICE_URL=$(kubectl get service threadstorm-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    if [ -z "$SERVICE_URL" ]; then
        print_warning "LoadBalancer IP not available yet"
        print_info "You may need to wait a few minutes for the LoadBalancer to be provisioned"
        return
    fi
    
    # Check health endpoint
    if curl -f -s http://$SERVICE_URL/health > /dev/null 2>&1; then
        print_status "Health check passed"
    else
        print_warning "Health check failed (service may still be starting)"
    fi
}

# Show deployment info
show_deployment_info() {
    print_info "Deployment Information:"
    echo ""
    
    echo "Namespace: $NAMESPACE"
    echo "Docker Image: $DOCKER_IMAGE"
    echo ""
    
    echo "Access URLs:"
    echo "  - Health Check: http://<load-balancer-ip>/health"
    echo "  - Main Application: http://<load-balancer-ip>/"
    echo "  - Admin Panel: http://<load-balancer-ip>/admin"
    echo "  - API Documentation: http://<load-balancer-ip>/docs"
    echo ""
    
    echo "Useful Commands:"
    echo "  - View logs: kubectl logs -f deployment/threadstorm -n $NAMESPACE"
    echo "  - Check status: kubectl get pods -n $NAMESPACE"
    echo "  - Scale deployment: kubectl scale deployment threadstorm --replicas=5 -n $NAMESPACE"
    echo "  - View events: kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'"
    echo ""
    
    echo "Logs:"
    echo "  - Deployment log: $LOG_FILE"
    echo "  - Application logs: kubectl logs -f deployment/threadstorm -n $NAMESPACE"
}

# Main deployment function
main() {
    echo "Starting Kubernetes deployment process..."
    echo ""
    
    check_prerequisites
    create_namespace
    setup_secrets
    deploy_redis
    deploy_threadstorm
    check_deployment
    health_check
    
    echo ""
    print_status "Kubernetes deployment completed successfully!"
    echo ""
    show_deployment_info
}

# Handle script arguments
case "${1:-}" in
    "deploy")
        main
        ;;
    "build")
        build_and_push_image
        ;;
    "secrets")
        setup_secrets
        ;;
    "redis")
        deploy_redis
        ;;
    "app")
        deploy_threadstorm
        ;;
    "status")
        check_deployment
        ;;
    "health")
        health_check
        ;;
    "logs")
        kubectl logs -f deployment/threadstorm -n $NAMESPACE
        ;;
    "scale")
        if [ -z "$2" ]; then
            echo "Usage: $0 scale <number-of-replicas>"
            exit 1
        fi
        kubectl scale deployment threadstorm --replicas=$2 -n $NAMESPACE
        print_status "Scaled to $2 replicas"
        ;;
    "delete")
        print_warning "This will delete all ThreadStorm resources!"
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kubectl delete namespace $NAMESPACE
            print_status "All resources deleted"
        else
            print_info "Deletion cancelled"
        fi
        ;;
    "upgrade")
        print_info "Upgrading ThreadStorm deployment..."
        kubectl rollout restart deployment/threadstorm -n $NAMESPACE
        kubectl rollout status deployment/threadstorm -n $NAMESPACE
        print_status "Upgrade completed"
        ;;
    *)
        echo "Usage: $0 {deploy|build|secrets|redis|app|status|health|logs|scale|delete|upgrade}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Complete deployment (namespace, secrets, redis, app)"
        echo "  build    - Build and push Docker image"
        echo "  secrets  - Setup secrets only"
        echo "  redis    - Deploy Redis only"
        echo "  app      - Deploy ThreadStorm app only"
        echo "  status   - Check deployment status"
        echo "  health   - Perform health check"
        echo "  logs     - View application logs"
        echo "  scale    - Scale deployment (e.g., $0 scale 5)"
        echo "  delete   - Delete all resources"
        echo "  upgrade  - Upgrade deployment"
        exit 1
        ;;
esac
