# 6. What was changed, known limits, troubleshooting

## 6.1 Problems found in the original project (and fixes)

| # | Problem | Fix |
|---|---|---|
| 1 | `requirements.txt` was saved as **UTF-16** and listed 150 packages (a full `pip freeze`). `pip install` in Docker fails on it. | Rewritten as UTF-8 with only the 8 direct dependencies, same versions. |
| 2 | `create_resume_pdf()` **never called `doc.build()`**, so no PDF was created and the download button would fail. | Fixed; the PDF is now built in memory and returned as bytes. |
| 3 | Text with `&` or `<` (e.g. "R&D") would crash ReportLab. | All text is XML-escaped. |
| 4 | Two different LLM clients (one in `app.py`, one in `models/ollama_client.py`). | One `llm.py`, address configurable. |
| 5 | Hard-coded `localhost` Ollama address and relative `storage/...` paths. | Environment-based config (`OLLAMA_BASE_URL`, `DATA_DIR`). |
| 6 | LLM or JSON errors crashed the page (`except:` with no type, no LLM error handling). | Specific error handling and friendly messages. |
| 7 | Real people's resumes/CVs, `__pycache__`, FAISS files were inside the project. | Excluded, and `.gitignore`/`.dockerignore` block them. Resumes are parsed from temporary files and deleted. |
| 8 | Dead files: `oldapp.py`, `ollamatest.py`, empty `rag/prompts.py`, empty `README.md`, mismatched folder names (`geverated_cv`, `activity_logs` vs `logs`). | Removed; layout simplified. (Your original zip is unchanged.) |
| 9 | No tests, no CI, Dockerfile ran as root and had no health check. | Added tests, CI/CD, non-root user, health check. |
| 10 | `.dockerignore` excluded a non-existent folder and copied everything else. | Rewritten. |

`activity_logger.py`, `cv_generator.py`, `rag/retriever.py`, `utils/*` were not used by the app. The useful parts were kept (`load_retriever` moved into `vector_store.py`); the rest can be added back when a feature needs it.

## 6.2 Known limits (be aware)

1. **The LLM does not run on free cloud tiers.** Options, from simplest:
   - *Matching-only public demo*: deploy as is. Skill matching works; LLM features show a warning.
   - *Your own Ollama*: run Ollama on your PC/server, expose it (Cloudflare Tunnel, Tailscale) and set `OLLAMA_BASE_URL`. Do not expose it to the open internet without authentication.
   - *Hosted model API*: replace `get_llm()` in `llm.py` (a paid API, usually cheap for a demo).
2. **Skill extraction is keyword based** (14 skills). Good for a demo; extend `SKILLS` or move to embedding similarity.
3. **FAISS index uses pickle** – only load indexes created by this app (`allow_dangerous_deserialization=True`). On Azure/AWS free tiers the container disk is temporary, so the index is lost on redeploy.
4. **No login**: anyone with the URL can use the app and see whatever they upload during their own session. Add authentication before using it with real candidate data.

## 6.3 Common local errors

| Error | Cause / fix |
|---|---|
| `ModuleNotFoundError: recruitme` | Run `pip install -e .` in the activated venv. |
| "Could not reach the LLM…" | `ollama serve` not running, or wrong `OLLAMA_BASE_URL`. |
| `model "llama3" not found` | `ollama pull llama3`. |
| `ruff` reports import order | `make format` fixes it automatically. |
| CI passes locally but fails on GitHub | Different Python version – test with 3.10 and 3.11. |
