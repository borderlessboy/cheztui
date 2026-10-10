.PHONY: check

# Everything CI checks except the packaging job. Run it before every push.
check:
	uv run ruff check .
	uv run ruff format --check .
	uv run ty check
	uv run pytest -q
