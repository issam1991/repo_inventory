#!/bin/bash

# Docker Deployment Script for Inventory Management System
# Run this on your Google Cloud VM

set -e

echo "🚀 Starting Docker deployment for Inventory Management System..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "Docker installed successfully!"
else
    echo "🐳 Docker is already installed"
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose installed successfully!"
else
    echo "🐳 Docker Compose is already installed"
fi

# Create app directory
APP_DIR="/opt/inventory-app"
echo "📁 Creating application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy application files (assuming they're uploaded to the VM)
echo "📋 Copying application files..."
# Note: You'll need to upload your files to the VM first
# You can use scp or git clone

# Build and start the application
echo "🔨 Building and starting the application..."
cd $APP_DIR

# Build the Docker image
echo "🏗️ Building Docker image..."
docker-compose build

# Start the services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Test the API
echo "🧪 Testing API endpoint..."
if curl -f http://localhost:5000/api/categories > /dev/null 2>&1; then
    echo "✅ API is working correctly!"
else
    echo "❌ API test failed"
fi

# Test the frontend
echo "🧪 Testing frontend..."
if curl -f http://localhost:8080/repo_inventory.html > /dev/null 2>&1; then
    echo "✅ Frontend is working correctly!"
else
    echo "❌ Frontend test failed"
fi

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 5000/tcp
sudo ufw allow 8080/tcp
sudo ufw --force enable

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Access Information:"
echo "   Frontend: http://$(curl -s ifconfig.me):8080/repo_inventory.html"
echo "   API: http://$(curl -s ifconfig.me):5000/api"
echo ""
echo "🔧 Useful Commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update application: docker-compose pull && docker-compose up -d"
echo ""
echo "💾 Database is persisted in: $APP_DIR/inventory.db"
