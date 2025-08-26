# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gunicorn \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application files
COPY app.py .
COPY repo_inventory.html .
COPY api_integration.js .
COPY inventory.db .

# Create a simple static file server script
RUN echo '#!/usr/bin/env python3\n\
import http.server\n\
import socketserver\n\
import os\n\
\n\
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):\n\
    def end_headers(self):\n\
        self.send_header("Access-Control-Allow-Origin", "*")\n\
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")\n\
        self.send_header("Access-Control-Allow-Headers", "Content-Type")\n\
        super().end_headers()\n\
    \n\
    def do_OPTIONS(self):\n\
        self.send_response(200)\n\
        self.end_headers()\n\
\n\
if __name__ == "__main__":\n\
    PORT = 8080\n\
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:\n\
        print(f"Serving static files at http://localhost:{PORT}")\n\
        httpd.serve_forever()' > static_server.py

# Make the static server script executable
RUN chmod +x static_server.py

# Create a startup script that runs both services
RUN echo '#!/bin/bash\n\
# Start Flask API with Gunicorn in background\n\
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app &\n\
\n\
# Start static file server\n\
python3 static_server.py' > start.sh

# Make startup script executable
RUN chmod +x start.sh

# Expose ports
EXPOSE 5000 8080

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the startup script
CMD ["./start.sh"]
