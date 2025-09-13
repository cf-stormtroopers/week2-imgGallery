.PHONY: help install dev run test clean lint format check-format

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run in development mode with auto-reload"
	@echo "  run         - Run the application"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean cache and build files"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code"
	@echo "  check-format - Check code formatting"
	@echo "  shell       - Open poetry shell"
	@echo "  install-dev - Install development dependencies"

# Install dependencies
install:
	poetry install

# Install development dependencies
install-dev:
	poetry install --with dev

# Run in development mode
dev:
	PYTHONUNBUFFERED=1 poetry run python src/start.py

# Run the application
run:
	poetry run python src/start.py

# Run tests
test:
	poetry run pytest tests/ -v

# Clean cache and build files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/

# Run linting
lint:
	poetry run flake8 src/
	poetry run mypy src/

# Format code
format:
	poetry run black src/
	poetry run isort src/

# Check formatting
check-format:
	poetry run black --check src/
	poetry run isort --check-only src/

# Open poetry shell
shell:
	poetry shell

# Database commands
db-migrate:
	@echo "Creating database tables..."
	poetry run python -c "from backend.config.database import create_db_and_tables; create_db_and_tables()"

# Development setup
setup-dev: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make dev' to start the development server"
