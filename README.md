# Tabular Insights Engine
**Deterministic, privacy-first LLM summaries for tabular data**

---

## Overview
Tabular Insights Engine is a production-ready scaffold for extracting compact samples from relational datasets, converting rows into LLM-friendly text, and producing deterministic, privacy-conscious summaries plus targeted follow-up questions. The project is designed to be lightweight, auditable, and deployable as a Streamlit demo or containerized microservice.

This README provides everything needed to understand, run, and extend the project: architecture, configuration, usage, testing, CI, security considerations, and contribution guidelines.

## Key features
- Sample data extraction from PostgreSQL with safe resource limits (e.g., `LIMIT`).
- Compact row-to-text formatting optimized for LLM input and token efficiency.
- Token-aware prompt design and truncation safeguards to avoid model limits.
- Deterministic summary generation and follow-up question creation.
- Streamlit-based demo, Docker containerization, CI pipeline, and pytest scaffolding.

## When to use
- Rapidly generate written summaries for small table snapshots.
- Produce human-readable follow-up questions to guide analysis or triage.
- Prototype LLM-assisted data review tools and lightweight analytics UIs.

---

## Repository layout
```
.
├── app.py                       # Streamlit demo launcher
├── flowchart_colored.mmd        # Mermaid source (flowchart)
├── architecture.mmd             # Mermaid architecture overview
├── Dockerfile
├── requirements.txt
├── .env.example
├── .github/
│   ├── workflows/ci.yml
│   └── dependabot.yml
├── tests/
├── FLOWCHART_DETAILED.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md                    # (this file)
```

## Architecture (summary)
The system is intentionally simple and composable:
- **UI / Launcher**: Streamlit app for demo and inspection.
- **Data Layer**: PostgreSQL provides tabular data. Queries are intentionally limited for previews.
- **Processing**: Rows are formatted into concise text, appended into a combined buffer, and truncated/chunked as needed to respect token limits.
- **LLM Integration**: A configured OpenRouter/OpenAI-compatible endpoint produces concise summaries and follow-up questions.
- **Optional infra**: Queue and worker components can be used for larger or async workloads (not required for the demo).

### Mermaid (flowchart)
The repository includes `flowchart_colored.mmd` — use a Mermaid renderer or VSCode plugin to preview. For documentation, `docs/flowchart_colored.png` shows a color-coded rendering of the processing flow.

---

## Quickstart — Local (development)

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd <repo-dir>
   ```

2. **Copy and populate environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and set DB_PASSWORD and OPENROUTER_API_KEY (or equivalent)
   ```

3. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run the Streamlit demo**
   ```bash
   streamlit run app.py
   ```
   Visit `http://localhost:8501` in your browser.

---

## Docker (containerized run)
Build and run the container locally (reads `.env` if passed via `--env-file`):
```bash
docker build -t tabular-insights-engine:latest .
docker run --env-file .env -p 8501:8501 tabular-insights-engine:latest
```

---

## Configuration & Environment
The project uses environment variables for secrets and endpoints. See `.env.example` for all keys. Important variables:
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `OPENROUTER_API_KEY` (or `OPENAI_API_KEY` if adapting)
- `OPENROUTER_BASE_URL` (default `https://openrouter.ai/api/v1`)
- `MODEL_NAME` (default `openai/gpt-3.5-turbo`)

**Security note**: Do not commit `.env` or credentials to git. Use a secrets manager for production.

---

## Development & Testing
- Unit tests use `pytest`. A basic smoke test is included in `tests/`.
  ```bash
  pytest -q
  ```
- Pre-commit hooks enforce formatting and basic checks (`.pre-commit-config.yaml` included).
- CI (`.github/workflows/ci.yml`) runs tests on push and PRs.

---

## CI / Release notes
- The supplied GitHub Actions workflow performs basic dependency installation and runs tests.
- Consider adding additional workflows for linting, release builds, or container scans.

---

## Operational considerations
- **Token management**: For larger tables implement chunking + map-reduce summarization. The current scaffold uses truncation to remain safe for small previews.
- **Retries & resilience**: Add exponential backoff and transient error handling on network calls to the LLM and DB.
- **Observability**: Integrate structured logging and metrics (e.g., Prometheus) for production. Avoid logging raw PII or secret content.
- **Rate limits & cost control**: For frequent use, batch requests or enforce sampling policies to reduce model usage.

---

## Contribution guidelines
See `CONTRIBUTING.md` for detailed processes. In brief:
- Open issues to discuss major changes.
- Create small, focused PRs with tests where applicable.
- Ensure code formatting with `black` and pre-commit hooks before submitting PRs.

---

## License
This project is released under the **MIT License** — see `LICENSE` for full text. Replace the license holder value with your organization if required.

---

## Contact & Support
For questions, issue reporting, or feature requests, open an issue in the repository. For organizational deployments, use your internal channels to manage secrets and access.

