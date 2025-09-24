.PHONY: help dev stop clean test build deploy demo demo-cli

help:
	@echo "Available commands:"
	@echo "  make dev    - Start development environment"
	@echo "  make demo   - Run demo API server (no Docker)"
	@echo "  make demo-cli - Demo CLI validation"
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

demo:
	@echo "🚀 Starting PolComply Demo API..."
	@echo "📝 API docs will be available at: http://localhost:8000/docs"
	@echo "🔍 Validation endpoint: POST http://localhost:8000/api/validate/xml"
	@echo "📊 Upload XML files to test FA-3 validation"
	@echo ""
	cd backend && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

demo-cli:
	@echo "🎯 PolComply CLI Demo"
	@echo "Testing FA-3 validation with sample files..."
	@echo ""
	cd polcomply && polcomply validate invoice tests/golden/fa3/valid_fv_b2b.xml --schema schemas/FA-3.xsd --report /tmp/report.html
	@echo ""
	@echo "✅ Report saved to: /tmp/report.html"
	@echo "Open in browser: open /tmp/report.html"