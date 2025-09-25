# BoxOfPorts - EJOIN Multi-WAN Router Management CLI
# Copyright (c) 2025 Althea Signals Network LLC. All rights reserved.
# 
# Professional Makefile for building, testing, and deploying bop

.PHONY: help install install-dev test test-all lint format clean run build docker-build docker-run docker-compose-up docker-compose-down package release deploy docs

# Project metadata
PROJECT_NAME := boxofports
VERSION := 1.0.0
AUTHOR := "Althea Signals Network LLC"
DOCKER_IMAGE := altheasignals/boxofports:$(VERSION)
DOCKER_LATEST := altheasignals/boxofports:latest

# Colors for output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

# Default target
help:
	@echo "$(BLUE)BoxOfPorts v$(VERSION) - EJOIN Multi-WAN Router Management CLI$(RESET)"
	@echo "$(BLUE)Developed by $(AUTHOR)$(RESET)"
	@echo ""
	@echo "$(GREEN)Available targets:$(RESET)"
	@echo "  $(YELLOW)Development:$(RESET)"
	@echo "    install       - Install package in development mode"
	@echo "    install-dev   - Install with development dependencies"
	@echo "    test          - Run unit tests"
	@echo "    test-all      - Run all tests including integration"
	@echo "    lint          - Run linting checks"
	@echo "    format        - Format code"
	@echo "    clean         - Clean build artifacts"
	@echo ""
	@echo "  $(YELLOW)Building & Distribution:$(RESET)"
	@echo "    build         - Build distribution packages"
	@echo "    package       - Create distribution package"
	@echo "    release       - Prepare for release"
	@echo ""
	@echo "  $(YELLOW)Docker Operations:$(RESET)"
	@echo "    docker-build  - Build Docker image"
	@echo "    docker-run    - Run Docker container"
	@echo "    docker-test   - Test Docker container"
	@echo "    compose-up    - Start with Docker Compose"
	@echo "    compose-down  - Stop Docker Compose services"
	@echo ""
	@echo "  $(YELLOW)Deployment:$(RESET)"
	@echo "    deploy-local  - Deploy locally"
	@echo "    deploy-docker - Deploy with Docker"
	@echo "    setup-dirs    - Setup directory structure"
	@echo ""
	@echo "  $(YELLOW)Utilities:$(RESET)"
	@echo "    run           - Run CLI with help"
	@echo "    docs          - Generate documentation"
	@echo "    version       - Show version information"

# Installation targets
install:
	@echo "$(GREEN)Installing $(PROJECT_NAME) in development mode...$(RESET)"
	pip install -e .
	@echo "$(GREEN)✓ Installation complete$(RESET)"

install-dev:
	@echo "$(GREEN)Installing $(PROJECT_NAME) with development dependencies...$(RESET)"
	pip install -e ".[dev]"
	@echo "$(GREEN)✓ Development installation complete$(RESET)"

# Testing targets
test:
	@echo "$(GREEN)Running unit tests...$(RESET)"
	pytest tests/test_ports.py tests/test_templating_simple.py -v
	@echo "$(GREEN)✓ Unit tests passed$(RESET)"

test-all:
	@echo "$(GREEN)Running all tests...$(RESET)"
	pytest tests/ -v --cov=boxofports --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ All tests completed$(RESET)"

test-integration:
	@echo "$(GREEN)Running integration tests...$(RESET)"
	pytest tests/ -v --integration
	@echo "$(GREEN)✓ Integration tests completed$(RESET)"

# Code quality targets
lint:
	@echo "$(GREEN)Running linting checks...$(RESET)"
	ruff check boxofports/ tests/
	mypy boxofports/ --ignore-missing-imports
	@echo "$(GREEN)✓ Linting checks passed$(RESET)"

format:
	@echo "$(GREEN)Formatting code...$(RESET)"
	ruff format boxofports/ tests/
	@echo "$(GREEN)✓ Code formatted$(RESET)"

# Clean up targets
clean:
	@echo "$(GREEN)Cleaning build artifacts...$(RESET)"
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.orig" -delete
	@echo "$(GREEN)✓ Cleanup complete$(RESET)"

# Build targets
build: clean
	@echo "$(GREEN)Building distribution packages...$(RESET)"
	python -m build
	@echo "$(GREEN)✓ Build complete$(RESET)"

package: build
	@echo "$(GREEN)Creating distribution package...$(RESET)"
	tar -czf $(PROJECT_NAME)-$(VERSION).tar.gz dist/ README.md LICENSE DEPLOYMENT.md
	@echo "$(GREEN)✓ Package created: $(PROJECT_NAME)-$(VERSION).tar.gz$(RESET)"

release: clean test-all lint
	@echo "$(GREEN)Preparing release v$(VERSION)...$(RESET)"
	python -m build
	@echo "$(GREEN)✓ Release ready$(RESET)"

# Docker targets
docker-build:
	@echo "$(GREEN)Building Docker image $(DOCKER_IMAGE)...$(RESET)"
	docker build -t $(DOCKER_IMAGE) -t $(DOCKER_LATEST) .
	@echo "$(GREEN)✓ Docker image built$(RESET)"

docker-run: docker-build
	@echo "$(GREEN)Running Docker container...$(RESET)"
	docker run --rm $(DOCKER_IMAGE)

docker-test: docker-build
	@echo "$(GREEN)Testing Docker container...$(RESET)"
	docker run --rm $(DOCKER_IMAGE) --help
	@echo "$(GREEN)✓ Docker tests passed$(RESET)"

# Docker Compose targets
compose-up: setup-dirs
	@echo "$(GREEN)Starting services with Docker Compose...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(RESET)"

compose-down:
	@echo "$(GREEN)Stopping Docker Compose services...$(RESET)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(RESET)"

compose-logs:
	@echo "$(GREEN)Showing Docker Compose logs...$(RESET)"
	docker-compose logs -f boxofports

# Deployment targets
setup-dirs:
	@echo "$(GREEN)Setting up directory structure...$(RESET)"
	mkdir -p data config logs
	cp server_access.csv config/gateways.csv.example 2>/dev/null || true
	@echo "$(GREEN)✓ Directories created$(RESET)"

deploy-local: install
	@echo "$(GREEN)Deploying locally...$(RESET)"
	@echo "$(PROJECT_NAME) is ready to use!"
	@echo "Try: boxofports --help"
	@echo "$(GREEN)✓ Local deployment complete$(RESET)"

deploy-docker: docker-build setup-dirs
	@echo "$(GREEN)Deploying with Docker...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)✓ Docker deployment complete$(RESET)"

# Utility targets
run:
	@echo "$(GREEN)Running $(PROJECT_NAME) CLI...$(RESET)"
	boxofports --help

version:
	@echo "$(BLUE)$(PROJECT_NAME) v$(VERSION)$(RESET)"
	@echo "$(BLUE)Developed by $(AUTHOR)$(RESET)"
	@python -c "import boxofports; print(f'Package version: {boxofports.__version__}')" 2>/dev/null || echo "Package not installed"

docs:
	@echo "$(GREEN)Documentation available:$(RESET)"
	@echo "  - README.md - Main documentation"
	@echo "  - DEPLOYMENT.md - Deployment instructions"
	@echo "  - USAGE_GUIDE.md - Complete usage guide"
	@echo "  - LICENSE - License information"

# Development convenience targets
dev-setup: install-dev
	@echo "$(GREEN)Development environment setup complete!$(RESET)"
	@echo "Try these commands:"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Check code quality"
	@echo "  make run      - Run the CLI"

check: lint test
	@echo "$(GREEN)✓ All checks passed$(RESET)"