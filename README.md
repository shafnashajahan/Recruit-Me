# RecruitMe – AI Career Assistant

A lightweight AI recruitment copilot with two modes:

- **Recruiter** – upload resumes (PDF) + paste a job description → skill match score, matched/missing skills, AI interview questions.
- **CV Builder** – enter your details + a target job description → a tailored, ATS-friendly CV as a downloadable PDF.

Built with Python, Streamlit, LangChain, Ollama (local LLM), FAISS and ReportLab.

## Quick start (local)

```bash
# 1. Install Ollama from https://ollama.com, then download the models once
ollama pull llama3
ollama pull nomic-embed-text
ollama serve                      # leave running

# 2. Set up the project
make install                      # creates .venv and installs everything
cp .env.example .env              # optional: change settings

# 3. Run
source .venv/bin/activate
streamlit run app/streamlit_app.py     # opens http://localhost:8501
```

No Make? Run: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt && pip install -e .`

**With Docker** (app + Ollama together): `docker compose up --build`, then pull the models (see comments in `docker-compose.yml`).

## Project layout

```
recruitme/
├── app/streamlit_app.py      # UI only – no business logic
├── src/recruitme/            # the application package
│   ├── config.py             # settings from environment variables
│   ├── llm.py                # the ONLY place that talks to Ollama
│   ├── parser.py             # PDF -> text
│   ├── skills.py             # skill extraction
│   ├── matcher.py            # match score
│   ├── interviewer.py        # interview questions
│   ├── cv_builder.py         # CV prompt, JSON parsing, PDF creation
│   └── vector_store.py       # FAISS index
├── tests/                    # automated tests (pytest)
├── docs/                     # step-by-step guides (start here!)
├── infra/                    # Azure & AWS setup scripts
├── .github/workflows/        # CI (test) and CD (deploy) pipelines
├── Dockerfile, docker-compose.yml
├── pyproject.toml, requirements*.txt, Makefile, .env.example
```

## Documentation

| # | Guide | What it covers |
|---|-------|----------------|
| 1 | [Project guide](docs/01-project-guide.md) | How the project is built and how to use it |
| 2 | [GitHub setup](docs/02-github-setup.md) | Git, repository, branches, secrets |
| 3 | [CI/CD explained](docs/03-cicd-explained.md) | What each pipeline step does |
| 4 | [Deploy to Azure](docs/04-deploy-azure.md) | Free-tier deployment, step by step |
| 5 | [Deploy to AWS](docs/05-deploy-aws.md) | Free-tier deployment, step by step |
| 6 | [Changes & troubleshooting](docs/06-changes-and-troubleshooting.md) | What was fixed, common errors |

## Development

```bash
make test     # run tests
make lint     # ruff check
```

Every push and pull request runs the same checks in GitHub Actions.
