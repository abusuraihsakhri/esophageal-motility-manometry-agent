# Esophageal Motility Manometry Agent

### [Open the Live Application →](https://abusuraihsakhri.github.io/esophageal-motility-manometry-agent/)

A Python CLI and FastAPI service for evaluating **generic demonstration rules** over two numeric inputs, an optional critical flag, and a descriptor. A standalone browser demo shows the same three rule triggers without requiring a server.

**Clinical limitation:** This repository is **not** a validated implementation of Chicago Classification v4.0 (CCv4.0). Its existing thresholds (primary metric >25, secondary metric >12) are illustrative, are not labeled with clinically meaningful units, and cannot classify achalasia, esophagogastric junction outflow obstruction, spasm, hypercontractile esophagus, or ineffective esophageal motility. Results must not be used for diagnosis, management, or patient triage.

CCv4.0 requires device- and position-specific IRP thresholds, swallow-level contractility and pressurization analysis, an appropriate HRM protocol, clinical context, and sometimes supportive testing. See [Yadlapati et al., *Neurogastroenterology & Motility* (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8034247/).

## Browser demonstration

The repository contains a static [browser application](index.html) with synthetic examples, three rule checks, a JSON result, and an export action. Open `index.html` directly in a modern browser, or serve the repository locally:

```bash
python -m http.server 8080
# Open http://localhost:8080/
```

The browser demo runs entirely in JavaScript: **no Python, API, or Pyodide is loaded**. It performs no cryptographic audit signing and does not transmit, store, or log entries to a server. Inputs remain in the tab; exported files are saved only by explicit user action. Use synthetic, non-identifying data only.

## Python installation and usage

Requires Python 3.9 or newer (CI tests Python 3.10–3.12).

```bash
git clone https://github.com/abusuraihsakhri/esophageal-motility-manometry-agent.git
cd esophageal-motility-manometry-agent
python -m pip install -e ".[api,test]"

python cli.py audit --task-id SYN-001 --target KEY-001 --primary 28.5 --secondary 14.2
python cli.py batch -i input.csv -o results.csv
python cli.py chat "What is the system status?"
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The package also includes the historical `manometry_mind.py` entry point and the `esophageal_motility_manometry_agent` package. They use different demonstration schemas and thresholds; they are retained for compatibility, not interchangeable clinical classifications.

### CSV batch format

```csv
task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag
SYN-001,KEY-001,28.5,14.2,DISCORDANT,true
SYN-002,KEY-002,10.0,3.2,NOMINAL,false
```

Output adds `overall_urgency`, `integrity_status`, `total_alerts`, and `audit_hash`. Malformed numeric records are marked `ERROR` without stopping the batch. For realistic patient datasets, additional privacy and safety engineering is required.

### REST API

Start with `python cli.py serve` and visit `http://127.0.0.1:8000/docs`. Routes are `GET /health`, `GET /metrics` (JSON counters), `POST /api/audit`, `POST /api/chat` (deterministic mock response), and `GET /api/audit/logs`. The endpoint accepts the same generic rule fields as the CLI.

No actual external LLM provider is contacted: the current `LLMFactory` returns a deterministic mock for every configured provider name.

## Security and privacy scope

The Python service has a pattern-based identifier guard and a chained HMAC-SHA256 audit ledger. These are **defense-in-depth demonstrations**, not certified PHI detection, comprehensive de-identification, HIPAA compliance, or secure clinical audit infrastructure. Direct identifiers outside the known patterns can be missed.

Audit entries and their secret key are held in process memory; logs do **not** persist across restarts. Verification detects changes to signed entries while they remain in memory. Configure `AUDIT_SECRET_KEY` via a deployment secret, not source code. The application's endpoint has no authentication or authorization; do not expose it publicly or submit real patient data.

For Docker Compose:

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

## Testing

```bash
python -m pytest -v
node --check web/app.js
node web/test.js
```

GitHub Actions installs the Python package and runs the Python test suite and Node browser-rule tests on each pull request and push to `master`. The browser has not been subjected to clinical validation or a real patient workflow.

## Technology and compatibility

Python 3.9+, Pydantic v2, FastAPI/Uvicorn (optional API), pytest, and dependency-free browser JavaScript/HTML/CSS. The web demo uses standard modern browser capabilities (ES2017+, Blob downloads). No server-side Python can execute on GitHub Pages; the static demo is intentionally written in JavaScript.

## License

MIT — see [LICENSE](LICENSE).
