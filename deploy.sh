#!/bin/bash

# Digital Ocean App Platform Deployment Script
# This script handles force rebuilds and cache clearing

set -e

echo "🚀 Starting Digital Ocean App Platform Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    print_error "doctl CLI is not installed. Please install it first:"
    echo "https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if user is authenticated
if ! doctl auth list &> /dev/null; then
    print_error "Not authenticated with Digital Ocean. Please run: doctl auth init"
    exit 1
fi

# Function to get app ID
get_app_id() {
    local app_name="kolekt"
    local app_id=$(doctl apps list --format ID,Spec.Name --no-header | grep "$app_name" | awk '{print $1}')
    
    if [ -z "$app_id" ]; then
        print_error "Could not find app with name: $app_name"
        print_status "Available apps:"
        doctl apps list --format ID,Spec.Name
        exit 1
    fi
    
    echo "$app_id"
}

# Function to force rebuild
force_rebuild() {
    local app_id=$1
    
    print_status "🔄 Initiating force rebuild for app ID: $app_id"
    
    # Create a temporary deployment with force rebuild
    doctl apps create-deployment "$app_id" --wait
    
    if [ $? -eq 0 ]; then
        print_success "Force rebuild completed successfully!"
    else
        print_error "Force rebuild failed!"
        exit 1
    fi
}

# Function to clear build cache (by updating app spec)
clear_cache() {
    local app_id=$1
    
    print_status "🧹 Clearing build cache..."
    
    # Get current app spec
    doctl apps get "$app_id" --format Spec > temp_app_spec.yaml
    
    # Add a timestamp to force cache invalidation
    timestamp=$(date +%s)
    sed -i.bak "s/version:.*/version: \"$timestamp\"/" temp_app_spec.yaml
    
    # Update the app with new spec
    doctl apps update "$app_id" --spec temp_app_spec.yaml
    
    # Clean up
    rm -f temp_app_spec.yaml temp_app_spec.yaml.bak
    
    print_success "Build cache cleared!"
}

# Function to monitor deployment
monitor_deployment() {
    local app_id=$1
    
    print_status "📊 Monitoring deployment status..."
    
    # Wait for deployment to complete
    while true; do
        status=$(doctl apps get "$app_id" --format Status.Phase --no-header)
        
        case $status in
            "RUNNING")
                print_success "✅ App is running successfully!"
                break
                ;;
            "DEPLOYING")
                print_status "⏳ Still deploying..."
                sleep 10
                ;;
            "ERROR")
                print_error "❌ Deployment failed!"
                doctl apps get "$app_id" --format Status.Message
                exit 1
                ;;
            *)
                print_status "Current status: $status"
                sleep 10
                ;;
        esac
    done
}

# Function to show app info
show_app_info() {
    local app_id=$1
    
    print_status "📋 App Information:"
    doctl apps get "$app_id" --format ID,Spec.Name,Status.Phase,Spec.Services[0].SourceBranch,Spec.Services[0].SourceRepo
    
    print_status "🌐 App URL:"
    doctl apps get "$app_id" --format Status.LiveURL --no-header
}

# Main deployment function
deploy() {
    local force_rebuild_flag=$1
    
    print_status "🔍 Finding your app..."
    local app_id=$(get_app_id)
    print_success "Found app ID: $app_id"
    
    # Show current app info
    show_app_info "$app_id"
    
    if [ "$force_rebuild_flag" = "true" ]; then
        print_warning "⚠️  Force rebuild mode enabled - this will clear build cache"
        
        # Clear cache first
        clear_cache "$app_id"
        
        # Force rebuild
        force_rebuild "$app_id"
    else
        print_status "📤 Pushing to git to trigger deployment..."
        git push
        
        if [ $? -eq 0 ]; then
            print_success "Git push successful! Deployment should start automatically."
        else
            print_error "Git push failed!"
            exit 1
        fi
    fi
    
    # Monitor deployment
    monitor_deployment "$app_id"
    
    # Show final app info
    print_success "🎉 Deployment completed!"
    show_app_info "$app_id"
}

# Parse command line arguments
case "${1:-}" in
    "force"|"--force"|"-f")
        deploy "true"
        ;;
    "help"|"--help"|"-h")
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  (no args)  - Normal deployment via git push"
        echo "  force      - Force rebuild with cache clearing"
        echo "  help       - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0          # Normal deployment"
        echo "  $0 force    # Force rebuild and clear cache"
        ;;
    "")
        deploy "false"
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
