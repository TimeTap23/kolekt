#!/bin/bash

# ThreadStorm Kubernetes Secrets Encoder
# This script helps encode your secrets for Kubernetes deployment

echo "🔐 ThreadStorm Kubernetes Secrets Encoder"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to encode a secret
encode_secret() {
    local name=$1
    local value=$2
    local encoded=$(echo -n "$value" | base64)
    echo "  $name: $encoded"
}

echo "Encoding secrets for Kubernetes..."
echo ""

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    print_warning ".env.production not found. Please create it first:"
    echo "cp env.production .env.production"
    echo "Then edit it with your actual values."
    exit 1
fi

# Source the environment file
source .env.production

echo "Copy the following encoded values to k8s/secrets.yaml:"
echo ""

# Required secrets
print_info "Required Secrets:"
echo "=================="

# Supabase Configuration
if [ ! -z "$SUPABASE_URL" ]; then
    encode_secret "supabase-url" "$SUPABASE_URL"
else
    print_warning "SUPABASE_URL not set"
fi

if [ ! -z "$SUPABASE_KEY" ]; then
    encode_secret "supabase-key" "$SUPABASE_KEY"
else
    print_warning "SUPABASE_KEY not set"
fi

if [ ! -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    encode_secret "supabase-service-role-key" "$SUPABASE_SERVICE_ROLE_KEY"
else
    print_warning "SUPABASE_SERVICE_ROLE_KEY not set"
fi

echo ""

# Meta/Threads API Configuration
print_info "Meta/Threads API Secrets:"
echo "============================"

if [ ! -z "$META_APP_ID" ]; then
    encode_secret "meta-app-id" "$META_APP_ID"
else
    print_warning "META_APP_ID not set"
fi

if [ ! -z "$META_APP_SECRET" ]; then
    encode_secret "meta-app-secret" "$META_APP_SECRET"
else
    print_warning "META_APP_SECRET not set"
fi

if [ ! -z "$THREADS_APP_ID" ]; then
    encode_secret "threads-app-id" "$THREADS_APP_ID"
else
    print_warning "THREADS_APP_ID not set"
fi

if [ ! -z "$THREADS_APP_SECRET" ]; then
    encode_secret "threads-app-secret" "$THREADS_APP_SECRET"
else
    print_warning "THREADS_APP_SECRET not set"
fi

echo ""

# Security Configuration
print_info "Security Secrets:"
echo "==================="

if [ ! -z "$SECRET_KEY" ]; then
    encode_secret "secret-key" "$SECRET_KEY"
else
    print_warning "SECRET_KEY not set"
fi

if [ ! -z "$TOKEN_ENCRYPTION_KEY" ]; then
    encode_secret "token-encryption-key" "$TOKEN_ENCRYPTION_KEY"
else
    print_warning "TOKEN_ENCRYPTION_KEY not set"
fi

echo ""

# Redis Configuration
print_info "Redis Configuration:"
echo "======================"

if [ ! -z "$REDIS_PASSWORD" ]; then
    encode_secret "redis-password" "$REDIS_PASSWORD"
else
    # Generate a secure Redis password
    REDIS_PASSWORD=$(openssl rand -base64 32)
    encode_secret "redis-password" "$REDIS_PASSWORD"
    print_info "Generated Redis password: $REDIS_PASSWORD"
fi

echo ""

# Optional AWS Configuration
print_info "Optional AWS Configuration:"
echo "=============================="

if [ ! -z "$AWS_ACCESS_KEY_ID" ]; then
    encode_secret "aws-access-key-id" "$AWS_ACCESS_KEY_ID"
else
    print_warning "AWS_ACCESS_KEY_ID not set (optional)"
fi

if [ ! -z "$AWS_SECRET_ACCESS_KEY" ]; then
    encode_secret "aws-secret-access-key" "$AWS_SECRET_ACCESS_KEY"
else
    print_warning "AWS_SECRET_ACCESS_KEY not set (optional)"
fi

if [ ! -z "$AWS_REGION" ]; then
    encode_secret "aws-region" "$AWS_REGION"
else
    print_warning "AWS_REGION not set (optional)"
fi

if [ ! -z "$AWS_KMS_KEY_ID" ]; then
    encode_secret "aws-kms-key-id" "$AWS_KMS_KEY_ID"
else
    print_warning "AWS_KMS_KEY_ID not set (optional)"
fi

echo ""

# Optional Email Configuration
print_info "Optional Email Configuration:"
echo "================================"

if [ ! -z "$SMTP_HOST" ]; then
    encode_secret "smtp-host" "$SMTP_HOST"
else
    print_warning "SMTP_HOST not set (optional)"
fi

if [ ! -z "$SMTP_USER" ]; then
    encode_secret "smtp-user" "$SMTP_USER"
else
    print_warning "SMTP_USER not set (optional)"
fi

if [ ! -z "$SMTP_PASSWORD" ]; then
    encode_secret "smtp-password" "$SMTP_PASSWORD"
else
    print_warning "SMTP_PASSWORD not set (optional)"
fi

echo ""

# Optional Monitoring Configuration
print_info "Optional Monitoring Configuration:"
echo "======================================"

if [ ! -z "$SENTRY_DSN" ]; then
    encode_secret "sentry-dsn" "$SENTRY_DSN"
else
    print_warning "SENTRY_DSN not set (optional)"
fi

if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
    encode_secret "slack-webhook-url" "$SLACK_WEBHOOK_URL"
else
    print_warning "SLACK_WEBHOOK_URL not set (optional)"
fi

if [ ! -z "$DISCORD_WEBHOOK_URL" ]; then
    encode_secret "discord-webhook-url" "$DISCORD_WEBHOOK_URL"
else
    print_warning "DISCORD_WEBHOOK_URL not set (optional)"
fi

echo ""
print_success "Secrets encoding complete!"
echo ""
print_info "Next steps:"
echo "1. Copy the encoded values above to k8s/secrets.yaml"
echo "2. Replace the placeholder values with the actual encoded values"
echo "3. Run: kubectl apply -f k8s/secrets.yaml"
echo "4. Deploy the application: kubectl apply -f k8s/deployment.yaml"
