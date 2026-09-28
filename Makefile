.PHONY: install run test lint format docker
install:  ## create venv and install everything
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt && pip install -e .
run:      ## start the app (Ollama must be running)
	streamlit run app/streamlit_app.py
test:
	pytest
lint:
	ruff check .
format:
	ruff check --fix . && ruff format .
docker:
	docker compose up --build
