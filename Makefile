.PHONY: help install setup run test test-verbose test-coverage clean

help:
	@echo "Available commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make setup            - Initialize the RAG system"
	@echo "  make run              - Start FastAPI server"
	@echo "  make test             - Run pytest tests"
	@echo "  make test-verbose     - Run tests with verbose output"
	@echo "  make test-coverage    - Run tests with coverage report"
	@echo "  make clean            - Remove cache and temp files"

install:
	pip install -e .

setup:
	python setup_rag.py

run:
	fastapi dev app/main.py

test:
	pytest tests/ -q

test-verbose:
	pytest tests/ -v

test-coverage:
	pip install coverage
	coverage run -m pytest tests/
	coverage report -m

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
