#!/bin/bash

# Decode Kubernetes secrets and set up environment variables for App Platform

echo "Decoding Kubernetes secrets..."

# Decode the base64 values
SUPABASE_URL=$(echo "aHR0cHM6Ly9jbmxvdWNtenVnbmt3c3pxZHhqbC5zdXBhYmFzZS5jbw==" | base64 -d)
SUPABASE_KEY=$(echo "ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKemRYQmhZbUZ6WlNJc0luSmxaaUk2SW1OdWJHOTFZMjE2ZFdkdWEzZHplbkZrZUdwc0lpd2ljbTlzWlNJNkluTmxjblpwWTJWZmNtOXNaU0lzSW1saGRDSTZNVGMxTlRBM05URXdOQ3dpWlhod0lqb3lNRGN3TmpVeE1UQTBmUS5tTUtpZzBabnY3V2h2NEdYMjd4ZFBLZXg3NGRHcWlhazRwd0tIeDEtZFRz" | base64 -d)
SUPABASE_SERVICE_ROLE_KEY=$(echo "ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SnBjM01pT2lKemRYQmhZbUZ6WlNJc0luSmxaaUk2SW1OdWJHOTFZMjE2ZFdkdWEzZHplbkZrZUdwc0lpd2ljbTlzWlNJNkluTmxjblpwWTJWZmNtOXNaU0lzSW1saGRDSTZNVGMxTlRBM05URXdOQ3dpWlhod0lqb3lNRGN3TmpVeE1UQTBmUS5tTUtpZzBabnY3V2h2NEdYMjd4ZFBLZXg3NGRHcWlhazRwd0tIeDEtZFRz" | base64 -d)
META_APP_ID=$(echo "MTQ3MzIyNzE4MDc2MDk4OQ==" | base64 -d)
META_APP_SECRET=$(echo "NDAwMWNiNzA1MzA5YzhhNzY2MTNmZjQ4MjUyZjVkZmQ=" | base64 -d)
THREADS_APP_ID=$(echo "NzM1Mzk2MzAyNjM3OTY5" | base64 -d)
THREADS_APP_SECRET=$(echo "M2JlMTg4ZDNjYzYyYmRmOTc2YzYyOTU3NmQyMjM1YmQ=" | base64 -d)
SECRET_KEY=$(echo "eW91ci1zdXBlci1zZWNyZXQtand0LWtleS1oZXJl" | base64 -d)
TOKEN_ENCRYPTION_KEY=$(echo "eW91ci0zMi1jaGFyYWN0ZXItZW5jcnlwdGlvbi1rZXk=" | base64 -d)
REDIS_PASSWORD=$(echo "UE1xUyt5cXYwZEc1MCtUTjVCL2JtT2ZUcW13OWRwR2kvalFKTS9RaXBXQT0=" | base64 -d)

echo "Environment variables decoded successfully!"
echo ""
echo "Use these values in your DigitalOcean App Platform deployment:"
echo ""
echo "SUPABASE_URL=$SUPABASE_URL"
echo "SUPABASE_KEY=$SUPABASE_KEY"
echo "SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY"
echo "META_APP_ID=$META_APP_ID"
echo "META_APP_SECRET=$META_APP_SECRET"
echo "THREADS_APP_ID=$THREADS_APP_ID"
echo "THREADS_APP_SECRET=$THREADS_APP_SECRET"
echo "SECRET_KEY=$SECRET_KEY"
echo "TOKEN_ENCRYPTION_KEY=$TOKEN_ENCRYPTION_KEY"
echo "REDIS_PASSWORD=$REDIS_PASSWORD"
echo ""
echo "Note: You'll also need to set REDIS_URL to your Redis instance URL"
