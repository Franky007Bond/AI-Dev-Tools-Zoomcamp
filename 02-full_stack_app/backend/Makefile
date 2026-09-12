.PHONY: help install run test

help:
	@echo "Waitly backend"
	@echo ""
	@echo "  make install   Install dependencies (uv sync)"
	@echo "  make run       Start API at http://localhost:8001/v1"
	@echo "  make test      Run pytest"

install:
	uv sync

run:
	uv run waitly-api

test:
	uv run pytest -v
