# ThreadStorm Makefile

.PHONY: help install dev test lint format clean docker-build docker-run docker-stop

# Default target
help:
	@echo "ThreadStorm - Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run development server"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  clean       - Clean cache and temporary files"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker services"
	@echo ""
	@echo "Database:"
	@echo "  db-migrate  - Run database migrations"
	@echo "  db-reset    - Reset database"
	@echo ""
	@echo "Production:"
	@echo "  prod-build  - Build for production"
	@echo "  prod-run    - Run production server"

# Development commands
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

dev:
	@echo "Starting development server..."
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "Running tests..."
	pytest tests/ -v

lint:
	@echo "Running linting..."
	flake8 src/ tests/
	mypy src/

format:
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/

clean:
	@echo "Cleaning cache and temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t threadstorm .

docker-run:
	@echo "Starting ThreadStorm with Docker Compose..."
	docker-compose up -d

docker-stop:
	@echo "Stopping Docker services..."
	docker-compose down

# Database commands
db-migrate:
	@echo "Running database migrations..."
	alembic upgrade head

db-reset:
	@echo "Resetting database..."
	alembic downgrade base
	alembic upgrade head

# Production commands
prod-build:
	@echo "Building for production..."
	docker build -t threadstorm:prod --target production .

prod-run:
	@echo "Running production server..."
	docker-compose -f docker-compose.yml --profile production up -d

# Utility commands
logs:
	@echo "Showing logs..."
	docker-compose logs -f

shell:
	@echo "Opening shell in container..."
	docker-compose exec threadstorm bash

# Setup commands
setup-dev:
	@echo "Setting up development environment..."
	cp env.example .env
	@echo "Please edit .env file with your configuration"
	@echo "Then run: make install"

setup-docker:
	@echo "Setting up Docker environment..."
	docker-compose up -d postgres redis
	@echo "Waiting for services to be ready..."
	sleep 10
	make db-migrate
	@echo "Docker environment ready!"
