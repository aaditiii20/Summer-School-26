#!/bin/bash

# AYUSH FHIR Terminology Portal - Deployment Script
# This script handles the complete deployment process

set -e  # Exit on any error

echo " Starting AYUSH FHIR Portal Deployment..."

# Configuration
APP_NAME="ayush-fhir-portal"
DOCKER_IMAGE="$APP_NAME:latest"
CONTAINER_NAME="$APP_NAME-container"
PORT=${PORT:-8000}
ENVIRONMENT=${ENVIRONMENT:-production}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is available"
}

# Check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs ssl data/backups
    print_success "Directories created"
}

# Generate self-signed SSL certificates (for development)
generate_ssl() {
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        print_status "Generating SSL certificates..."
        mkdir -p ssl
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
            -subj "/C=IN/ST=India/L=City/O=AYUSH/OU=FHIR/CN=localhost"
        print_success "SSL certificates generated"
    else
        print_success "SSL certificates already exist"
    fi
}

# Build Docker image
build_image() {
    print_status "Building Docker image..."
    docker build -t $DOCKER_IMAGE .
    print_success "Docker image built successfully"
}

# Stop existing containers
stop_containers() {
    print_status "Stopping existing containers..."
    docker-compose down --remove-orphans || true
    print_success "Existing containers stopped"
}

# Start services
start_services() {
    print_status "Starting services..."
    docker-compose up -d
    print_success "Services started successfully"
}

# Wait for services to be healthy
wait_for_health() {
    print_status "Waiting for services to be healthy..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:$PORT/health &> /dev/null; then
            print_success "Service is healthy"
            return 0
        fi
        print_warning "Attempt $attempt/$max_attempts: Service not ready yet..."
        sleep 10
        ((attempt++))
    done
    
    print_error "Service failed to become healthy"
    return 1
}

# Show deployment status
show_status() {
    print_status "Deployment Status:"
    echo "----------------------------------------"
    echo " Portal URL: https://localhost"
    echo " API Docs: https://localhost/docs"
    echo " Health Check: https://localhost/health"
    echo " Container Status:"
    docker-compose ps
    echo "----------------------------------------"
}

# Show logs
show_logs() {
    if [ "$1" = "--logs" ]; then
        print_status "Showing recent logs..."
        docker-compose logs --tail=50 -f
    fi
}

# Backup data
backup_data() {
    if [ "$1" = "--backup" ]; then
        print_status "Creating data backup..."
        timestamp=$(date +"%Y%m%d_%H%M%S")
        backup_file="data/backups/backup_$timestamp.tar.gz"
        tar -czf $backup_file data/ --exclude=data/backups
        print_success "Backup created: $backup_file"
    fi
}

# Main deployment function
deploy() {
    print_status " Starting AYUSH FHIR Portal Deployment"
    
    check_docker
    check_docker_compose
    create_directories
    generate_ssl
    stop_containers
    build_image
    start_services
    wait_for_health
    show_status
    
    print_success " Deployment completed successfully!"
    print_status "Access your portal at: https://localhost"
}

# Parse command line arguments
case "$1" in
    "deploy")
        deploy
        ;;
    "start")
        start_services
        show_status
        ;;
    "stop")
        stop_containers
        ;;
    "restart")
        stop_containers
        start_services
        wait_for_health
        show_status
        ;;
    "logs")
        show_logs --logs
        ;;
    "status")
        show_status
        ;;
    "backup")
        backup_data --backup
        ;;
    "build")
        build_image
        ;;
    *)
        echo "Usage: $0 {deploy|start|stop|restart|logs|status|backup|build}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Full deployment (build, start, configure)"
        echo "  start    - Start services"
        echo "  stop     - Stop services"
        echo "  restart  - Restart services"
        echo "  logs     - Show service logs"
        echo "  status   - Show deployment status"
        echo "  backup   - Create data backup"
        echo "  build    - Build Docker image"
        exit 1
        ;;
esac
