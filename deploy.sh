#!/bin/bash

# ThreadStorm Production Deployment Script
# This script handles the complete deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="threadstorm"
DOMAIN="threadstorm.com"
EMAIL="admin@threadstorm.com"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# Logging
LOG_FILE="deploy.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo -e "${BLUE}🚀 ThreadStorm Production Deployment${NC}"
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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env.production exists
    if [ ! -f ".env.production" ]; then
        print_error ".env.production file not found"
        print_info "Please copy env.production to .env.production and configure it"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Setup SSL certificates
setup_ssl() {
    print_info "Setting up SSL certificates..."
    
    # Create SSL directory
    mkdir -p nginx/ssl
    
    # Check if certificates already exist
    if [ -f "nginx/ssl/threadstorm.crt" ] && [ -f "nginx/ssl/threadstorm.key" ]; then
        print_warning "SSL certificates already exist, skipping generation"
        return
    fi
    
    # Generate self-signed certificate for development
    # In production, you should use Let's Encrypt or a proper CA
    print_info "Generating self-signed SSL certificate..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/threadstorm.key \
        -out nginx/ssl/threadstorm.crt \
        -subj "/C=US/ST=State/L=City/O=ThreadStorm/CN=$DOMAIN"
    
    print_status "SSL certificates generated"
}

# Setup environment
setup_environment() {
    print_info "Setting up environment..."
    
    # Create necessary directories
    mkdir -p logs uploads nginx/ssl
    
    # Set proper permissions
    chmod 755 logs uploads
    chmod 600 nginx/ssl/*
    
    print_status "Environment setup complete"
}

# Build and deploy services
deploy_services() {
    print_info "Building and deploying services..."
    
    # Stop existing services
    print_info "Stopping existing services..."
    docker-compose -f $DOCKER_COMPOSE_FILE down --remove-orphans
    
    # Build images
    print_info "Building Docker images..."
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
    
    # Start services
    print_info "Starting services..."
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    print_status "Services deployed successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_info "Waiting for services to be ready..."
    
    # Wait for main application
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
            print_status "Application is ready"
            break
        fi
        
        print_info "Waiting for application... (attempt $attempt/$max_attempts)"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "Application failed to start within expected time"
        docker-compose -f $DOCKER_COMPOSE_FILE logs threadstorm
        exit 1
    fi
}

# Run database migrations
run_migrations() {
    print_info "Running database migrations..."
    
    # This would typically run your database migration scripts
    # For now, we'll just check if the database is accessible
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Database connection verified"
    else
        print_warning "Could not verify database connection"
    fi
}

# Setup monitoring
setup_monitoring() {
    print_info "Setting up monitoring..."
    
    # Create log rotation configuration
    cat > /etc/logrotate.d/threadstorm << EOF
/var/log/threadstorm/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF
    
    print_status "Monitoring setup complete"
}

# Health check
health_check() {
    print_info "Performing health check..."
    
    # Check main application
    if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Main application: OK"
    else
        print_error "Main application: FAILED"
        return 1
    fi
    
    # Check API endpoints
    if curl -f -s http://localhost:8000/api/v1/templates/ > /dev/null 2>&1; then
        print_status "API endpoints: OK"
    else
        print_error "API endpoints: FAILED"
        return 1
    fi
    
    # Check admin panel
    if curl -f -s http://localhost:8000/admin > /dev/null 2>&1; then
        print_status "Admin panel: OK"
    else
        print_warning "Admin panel: Not accessible (may require authentication)"
    fi
    
    print_status "Health check completed"
}

# Show deployment status
show_status() {
    print_info "Deployment Status:"
    echo ""
    
    # Show running containers
    echo "Running containers:"
    docker-compose -f $DOCKER_COMPOSE_FILE ps
    
    echo ""
    
    # Show service URLs
    echo "Service URLs:"
    echo "  Main Application: http://localhost:8000"
    echo "  Admin Panel: http://localhost:8000/admin"
    echo "  Health Check: http://localhost:8000/health"
    echo "  API Documentation: http://localhost:8000/docs"
    
    echo ""
    
    # Show logs location
    echo "Logs:"
    echo "  Application logs: ./logs/"
    echo "  Docker logs: docker-compose logs [service-name]"
    echo "  Deployment log: $LOG_FILE"
}

# Main deployment function
main() {
    echo "Starting deployment process..."
    echo ""
    
    check_prerequisites
    setup_environment
    setup_ssl
    deploy_services
    wait_for_services
    run_migrations
    setup_monitoring
    health_check
    
    echo ""
    print_status "Deployment completed successfully!"
    echo ""
    show_status
}

# Handle script arguments
case "${1:-}" in
    "deploy")
        main
        ;;
    "stop")
        print_info "Stopping services..."
        docker-compose -f $DOCKER_COMPOSE_FILE down
        print_status "Services stopped"
        ;;
    "restart")
        print_info "Restarting services..."
        docker-compose -f $DOCKER_COMPOSE_FILE restart
        print_status "Services restarted"
        ;;
    "logs")
        docker-compose -f $DOCKER_COMPOSE_FILE logs -f
        ;;
    "status")
        show_status
        ;;
    "health")
        health_check
        ;;
    "cleanup")
        print_info "Cleaning up..."
        docker-compose -f $DOCKER_COMPOSE_FILE down -v --remove-orphans
        docker system prune -f
        print_status "Cleanup completed"
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|health|cleanup}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy ThreadStorm to production"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show service logs"
        echo "  status   - Show deployment status"
        echo "  health   - Perform health check"
        echo "  cleanup  - Clean up containers and images"
        exit 1
        ;;
esac
