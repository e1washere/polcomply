.PHONY: help dev stop clean test build deploy

help:
	@echo "Available commands:"
	@echo "  make dev    - Start development environment"
	@echo "  make stop   - Stop all containers"
	@echo "  make clean  - Clean up containers and volumes"
	@echo "  make test   - Run tests"
	@echo "  make build  - Build production images"
	@echo "  make deploy - Deploy to production"

dev:
	@echo "Starting development environment..."
	@cp .env.example .env 2>/dev/null || true
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Running database migrations..."
	docker-compose exec backend alembic upgrade head
	@echo "\n✅ Development environment is ready!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000/docs"
	@echo "Database: localhost:5432"

stop:
	docker-compose down

clean:
	docker-compose down -v
	rm -rf backend/__pycache__
	rm -rf frontend/.next
	rm -rf frontend/node_modules

test:
	docker-compose exec backend pytest
	docker-compose exec frontend npm test

build:
	docker build -t polcomply-backend:latest ./backend
	docker build -t polcomply-frontend:latest ./frontend

deploy:
	@echo "Deploying to production..."
	./scripts/deploy.sh