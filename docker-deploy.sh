#!/bin/bash

# Docker Deployment Script for Inventory Management System
# Run this on your Google Cloud VM

set -e

echo "🚀 Starting Docker deployment for Inventory Management System..."


# Create app directory
APP_DIR="./"
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
