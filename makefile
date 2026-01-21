.PHONY: install format run dev

install:
	uv sync

format:
	uv run ruff format .

run:
	uv run streamlit run streamlit_app.py