# Docker Deployment Guide

This guide provides a simple Docker-based deployment solution for the Inventory Management System.

## 🐳 Overview

The Docker solution includes:
- **Single Container**: Flask API + Static File Server
- **Gunicorn**: Production WSGI server for Flask
- **Volume Persistence**: Database persists between container restarts
- **Health Checks**: Automatic service monitoring
- **Easy Management**: Simple docker-compose commands

## 📁 Files Created

- `Dockerfile` - Container definition
- `docker-compose.yml` - Multi-service orchestration
- `.dockerignore` - Build optimization
- `docker-deploy.sh` - VM deployment script
- `docker-upload.sh` - File upload script
- `DOCKER-DEPLOYMENT.md` - This guide

## 🚀 Quick Deployment

### Option 1: Automated Deployment (Recommended)

1. **Upload files to VM:**
   ```bash
   chmod +x docker-upload.sh
   ./docker-upload.sh
   ```

2. **Deploy on VM:**
   ```bash
   ssh 35.208.92.137
   cd /opt/inventory-app
   ./docker-deploy.sh
   ```

### Option 2: Manual Deployment

1. **On your local machine:**
   ```bash
   # Upload files manually
   scp Dockerfile docker-compose.yml app.py requirements.txt repo_inventory.html api_integration.js inventory.db 35.208.92.137:/opt/inventory-app/
   ```

2. **On the VM:**
   ```bash
   ssh 35.208.92.137
   cd /opt/inventory-app
   
   # Install Docker (if not installed)
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   
   # Build and start
   docker-compose up -d
   ```

## 🌐 Access URLs

After deployment, access your application at:

- **Frontend**: `http://35.208.92.137:8080/repo_inventory.html`
- **API**: `http://35.208.92.137:5000/api`

## 🔧 Management Commands

### View logs
```bash
docker-compose logs -f
```

### Stop services
```bash
docker-compose down
```

### Restart services
```bash
docker-compose restart
```

### Update application
```bash
docker-compose pull
docker-compose up -d
```

### Check service status
```bash
docker-compose ps
```

### Access container shell
```bash
docker-compose exec inventory-app bash
```

## 📊 Architecture

```
┌─────────────────────────────────────┐
│           Docker Container          │
├─────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  │
│  │   Gunicorn  │  │ Static File  │  │
│  │   Flask API │  │   Server     │  │
│  │   Port 5000 │  │  Port 8080   │  │
│  └─────────────┘  └──────────────┘  │
│  ┌─────────────────────────────────┐ │
│  │      SQLite Database           │ │
│  │    (Persisted via Volume)      │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## 🔒 Security Features

- **CORS Headers**: Properly configured for cross-origin requests
- **Production WSGI**: Gunicorn instead of Flask development server
- **Container Isolation**: Application runs in isolated environment
- **Firewall Rules**: Automatic UFW configuration

## 📈 Performance Features

- **Multi-worker Gunicorn**: 2 worker processes for better concurrency
- **Static File Caching**: Efficient static file serving
- **Health Checks**: Automatic service monitoring
- **Resource Optimization**: Slim Python base image

## 🛠️ Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs

# Check if ports are available
sudo netstat -tlnp | grep :5000
sudo netstat -tlnp | grep :8080
```

### Database issues
```bash
# Check database file permissions
ls -la inventory.db

# Access container to debug
docker-compose exec inventory-app bash
sqlite3 inventory.db ".tables"
```

### Frontend not loading
```bash
# Check if static files are served
curl http://localhost:8080/repo_inventory.html

# Check container logs
docker-compose logs inventory-app
```

### API not responding
```bash
# Test API directly
curl http://localhost:5000/api/categories

# Check Gunicorn logs
docker-compose logs inventory-app | grep gunicorn
```

## 🔄 Updates and Maintenance

### Update application code
1. Upload new files to VM
2. Rebuild and restart:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

### Backup database
```bash
# Copy database from container
docker cp inventory-management:/app/inventory.db ./inventory_backup.db
```

### Monitor resource usage
```bash
# Check container stats
docker stats inventory-management

# Check disk usage
docker system df
```

## 🎯 Benefits of Docker Solution

✅ **Simple Deployment**: One command to deploy everything
✅ **Consistent Environment**: Same setup across all environments
✅ **Easy Updates**: Simple rebuild and restart process
✅ **Resource Efficient**: Single container for both services
✅ **Production Ready**: Gunicorn, health checks, proper networking
✅ **Data Persistence**: Database survives container restarts
✅ **Easy Scaling**: Can easily add more containers if needed

## 📝 Notes

- The database file (`inventory.db`) is mounted as a volume to persist data
- Both API (port 5000) and frontend (port 8080) are exposed
- CORS is properly configured for cross-origin requests
- The application uses Gunicorn for production-grade serving
- Health checks ensure the application is running correctly

## 🆘 Support

If you encounter any issues:

1. Check the logs: `docker-compose logs -f`
2. Verify firewall settings: `sudo ufw status`
3. Test connectivity: `curl http://localhost:5000/api/categories`
4. Check container status: `docker-compose ps`
