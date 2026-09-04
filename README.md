# Esophageal Motility Manometry Agent

> **Domain:** Gastroenterology & Hepatology Systems
> **Standard:** AASLD / ACG / Chicago Classification v4.0

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Esophageal Motility Manometry Agent** is an advanced analytical platform implementing Chicago Classification v4.0 High-Resolution Manometry analysis. It analyzes integrated relaxation pressure (IRP), distal contractile integral (DCI), and classifies esophageal motility disorders including Achalasia (Types I-III), Jackhammer esophagus, and Ineffective Esophageal Motility (IEM).

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Core Evaluation Engines

- **`IRPRelaxationEvaluatorAgent`** — Evaluates integrated relaxation pressure against clinical baselines
- **`ContractileWaveAnalyzerAgent`** — Analyzes contractile wave patterns and STAT escalation triggers
- **`ChicagoV4ClassifierAgent`** — Classifies phenotypic discordance per Chicago Classification v4.0
- **`ManometryCoordinator`** — Executive coordinator orchestrating multi-agent consensus

### 🛡️ Enterprise Security

- **Zero-PHI Outbound Guard** — AST and regex inspection blocking SSNs, MRNs, phone numbers, emails, DOBs, and patient identifiers
- **HMAC-SHA256 Audit Trail** — Chained, cryptographically signed logs for every evaluation and state transition
- **Input Validation** — Sanitization and bounds checking on all inputs

### 🔌 Integration & Telemetry

- **LLM Reasoning Adapter** — Agnostic integration for local Ollama instances, Claude, GPT-4o, and deterministic test mocks
- **FastAPI REST API** — OpenAPI 3.1 REST endpoints for programmatic access
- **Prometheus Metrics** — Operational telemetry exporter (`/metrics`)

---

## 💻 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/esophageal-motility-manometry-agent.git
cd esophageal-motility-manometry-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

### Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `AUDIT_SECRET_KEY` | Secret key for HMAC-SHA256 audit trail signing | Random ephemeral key (set for production) |

---

## 🚀 Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i input.csv -o results.csv
```

### 4. Query the Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 5. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 6. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task/case identifier
- `--target`: Target entity or specimen key
- `--primary`: Primary metric measurement (float)
- `--secondary`: Secondary metric measurement (float)
- `--critical`: Flag for critical/emergency escalation
- `--status`: Status descriptor (e.g., NOMINAL, DISCORDANT)

### Input Data Schema (CSV Batch)

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Required |
| `target_identifier` | Target entity key | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary measurement value | Optional (default: 0.0) |
| `status_descriptor` | Status code or phenotype | Optional (default: NOMINAL) |
| `is_critical_flag` | Emergency escalation flag | Optional (default: false) |

---

## 🧪 Testing & Verification

Run the complete test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t esophageal-motility-manometry-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key esophageal-motility-manometry-agent
```

---

## 📁 Project Structure

```
esophageal-motility-manometry-agent/
├── agents/                          # Enterprise agent package
│   ├── api.py                       # FastAPI REST server
│   ├── base.py                      # Security, PHI guard, audit trail
│   ├── learning.py                  # Bayesian calibration engine
│   ├── llm_factory.py               # LLM provider factory
│   ├── metrics.py                   # Prometheus metrics collector
│   ├── models.py                    # Pydantic data models
│   ├── streamer.py                  # WebSocket telemetry broadcaster
│   ├── supervisor.py                # Master orchestrator
│   └── workers.py                   # Specialized domain workers
├── esophageal_motility_manometry_agent/  # Clinical package
│   ├── agents.py                    # Clinical sub-agents
│   ├── cli.py                       # Clinical CLI
│   ├── engine.py                    # Clinical algorithmic engine
│   ├── models.py                    # Clinical data models
│   └── server.py                    # Clinical FastAPI server
├── tests/                           # Test suite
│   ├── test_enrichment.py           # Enrichment module tests
│   ├── test_esophageal_motility_manometry_agent.py  # Core tests
│   └── test_security_and_reliability.py  # Security & reliability tests
├── cli.py                           # Main CLI entry point
├── manometry_mind.py                # Standalone manometry module
├── enrichment.py                    # Enrichment feature engines
├── simulator.py                     # High-throughput stress tester
├── pyproject.toml                   # Project configuration
├── Dockerfile                       # Container definition
└── docker-compose.yml               # Multi-service orchestration
```

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
