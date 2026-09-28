# 1. Project guide – how it is built and how to use it

## 1.1 What the app does

**Recruiter mode**
1. You upload one or more PDF resumes and paste a job description (JD).
2. The app extracts text from each PDF (`parser.py`) and finds known skills in both the resume and the JD (`skills.py`).
3. `matcher.py` calculates `score = matched skills / JD skills × 100`.
4. If Ollama is running, `interviewer.py` asks the LLM for technical, project and behavioural questions.
5. All texts are embedded and stored in a FAISS index (`vector_store.py`) for future search features.

**CV Builder mode**
1. You type your details and paste a target JD.
2. `cv_builder.py` builds a prompt; the LLM returns a JSON CV; the JSON is rendered to a PDF with ReportLab.
3. You download the PDF. Nothing is stored on the server.

## 1.2 Why the code is organised this way ("professional structure")

| Principle | How it appears here |
|---|---|
| **Separation of concerns** | UI (`app/`) is separate from logic (`src/recruitme/`). Logic can be tested without opening a browser. |
| **`src/` layout + `pyproject.toml`** | The code installs as a real package (`pip install -e .`); imports are `from recruitme.matcher import ...` everywhere. |
| **Configuration via environment** | `config.py` reads env vars (`OLLAMA_BASE_URL`, `LLM_MODEL`, …). The same code runs on laptop, Docker, Azure and AWS. |
| **One place for the LLM** | Only `llm.py` imports LangChain/Ollama for chat. To move to a hosted model later you edit one file. |
| **Graceful failure** | If the LLM is unreachable the UI shows a message instead of crashing; skill matching still works. |
| **Automated tests** | `tests/` covers matching, skills, CV JSON parsing, PDF creation, config and LLM error handling. |
| **Reproducible builds** | Pinned `requirements.txt`, a Dockerfile, and CI that rebuilds everything on every push. |
| **Privacy by default** | Resumes are parsed from temporary files and deleted; `.gitignore` blocks PDFs and `data/` from GitHub. |

## 1.3 Run it on your computer

Prerequisites: Python 3.10+ (3.11 recommended), Git, [Ollama](https://ollama.com).

```bash
ollama pull llama3
ollama pull nomic-embed-text
ollama serve                                # terminal 1, leave running

git clone <your-repo-url> && cd recruitme   # terminal 2
python -m venv .venv
source .venv/bin/activate                   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .
streamlit run app/streamlit_app.py
```

Open http://localhost:8501.

## 1.4 Configuration reference

| Variable | Default | Meaning |
|---|---|---|
| `LLM_MODEL` | `llama3` | Ollama chat model |
| `EMBED_MODEL` | `nomic-embed-text` | Ollama embedding model |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Where the Ollama server is |
| `LLM_TEMPERATURE` | `0` | 0 = most repeatable answers |
| `DATA_DIR` | `data` | Where the FAISS index is saved |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, … |

Set them in a `.env` file (copy `.env.example`) or in your shell / cloud settings.

## 1.5 Everyday developer workflow

```bash
git checkout -b feature/my-change     # never work directly on main
# ... edit code, add a test in tests/ ...
make test && make lint
git add -A && git commit -m "feat: describe the change"
git push -u origin feature/my-change  # then open a Pull Request on GitHub
```
CI runs automatically on the Pull Request. When it is green and the PR is merged into `main`, CD deploys (see guide 3).

## 1.6 Extending the project

- **More skills:** add words to `SKILLS` in `skills.py`, add a test.
- **Semantic ranking (roadmap in the old readme):** use `load_retriever()` in `vector_store.py`, rank resumes by similarity to the JD.
- **Hosted LLM:** change `get_llm()` in `llm.py`; nothing else needs to change.
