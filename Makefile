install:
	uv sync

run:
	uv run valuta

lint:
	uv run ruff check .

format:
	uv run ruff format .

build:
	uv build
