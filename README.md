# Centralized Social Media OSINT Manager

## Platform Overview
The Centralized Social Media OSINT Manager orchestrates open-source intelligence (OSINT) collection and engagement workflows across multiple social media and messaging platforms. The platform is designed to help analysts, growth teams, and compliance officers:

- Automate data collection from public and semi-public social channels.
- Classify, enrich, and prioritize leads with embedded AI/ML models.
- Trigger outbound engagement or escalation playbooks based on analyst-defined rules.
- Provide decision-makers with real-time dashboards, audit trails, and collaboration tooling.

## Core Modules
| Module | Purpose |
| --- | --- |
| **Crawler Service** | Connectors that collect profiles, posts, messages, and metadata from target platforms while respecting rate limits and legal constraints. Supports scheduled crawls, incremental updates, and lead qualification heuristics. |
| **Automation Engine** | Rule-based and ML-assisted workflows that react to crawler events. Handles deduplication, enrichment (LLM summarization, sentiment analysis), and triggers outbound actions such as notifications or engagement sequences. |
| **Analytics Pipeline** | Streaming and batch analytics for aggregations, dashboards, anomaly detection, and campaign KPI tracking. Exposes queryable datasets to BI tools. |
| **User Interface (UI)** | Web dashboard for campaign orchestration, case management, alert triage, and drill-down investigations. Integrates live metrics from the analytics pipeline and configuration tools for the crawler and automation engine. |

## Architecture Overview
```
+---------------------+          +--------------------+
|  Web Frontend (UI)  | <------> |  Backend API Gate  |
+---------------------+          +--------------------+
             ^                               |
             | GraphQL/REST                  |
             |                               v
      +--------------+              +---------------------+
      | Auth Service |              | Automation Engine   |
      +--------------+              +----------+----------+
             |                               |
             |                               v
      +--------------+               +---------------+
      |  Data Lake   | <-----------  | Crawler Pods  |
      +--------------+      Raw OSINT|               |
             ^                               |
             |                               v
      +--------------+               +---------------+
      | Analytics &  |  <----------  | External APIs |
      | ML Services  |     Events    +---------------+
      +--------------+
```

### Key Repository Locations
> As modules are implemented, the repository is organized into the following top-level directories:

- `backend/` – FastAPI/GraphQL services, automation engine, task scheduler, and Celery workers.
- `services/crawler/` – Platform-specific crawlers, connector SDKs, and scraping utilities.
- `analytics/` – Stream processors (Flink/Kafka Streams), feature engineering notebooks, and ML model packs.
- `frontend/` – React/Next.js user interface and component library.
- `infrastructure/` – IaC templates (Terraform), Kubernetes manifests, and deployment scripts.
- `docs/architecture/` – Source files for the architecture diagram (e.g., `architecture-overview.png`) and ADRs.

## Prerequisites
| Requirement | Recommended Specification |
| --- | --- |
| **CPU** | 8+ vCPU for development clusters; 4+ vCPU for lightweight/local mode. |
| **GPU (optional)** | NVIDIA RTX 3060 (12 GB) or better for local LLM inference. CPU-only fallback supported with reduced throughput. |
| **Memory** | 32 GB RAM when running local vector databases + LLMs; 16 GB minimum without ML workloads. |
| **Storage** | 50 GB free disk for datasets, models, and container caches. |
| **Python** | 3.10 or 3.11 (managed via `pyenv`/`asdf`). |
| **Node.js** | 18.x LTS (managed via `nvm`/`asdf`). |
| **Package Managers** | `pip`, `npm`, and optionally `poetry`/`pnpm` if your workflow requires them. |
| **Databases** | PostgreSQL 14+, Redis 6+, and (optional) OpenSearch/Elasticsearch 8+ for full-text indexing. |

## Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/<org>/crentralizied-Social-Media-OSINT-Manger.git
   cd crentralizied-Social-Media-OSINT-Manger
   ```
2. **Set up Python environment**
   ```bash
   pyenv install 3.11.6  # or use your preferred version manager
   pyenv virtualenv 3.11.6 osint-manager
   pyenv local osint-manager
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
3. **Set up Node.js environment for the frontend**
   ```bash
   nvm install 18
   nvm use 18
   cd frontend
   npm install
   cd ..
   ```
4. **Configure environment variables** – copy `.env.example` to `.env` in both `backend/` and `frontend/` (see below for details) and populate secrets (API keys, database URLs, JWT secrets).
5. **Provision local dependencies** – ensure PostgreSQL, Redis, and (optional) OpenSearch/Vector DB (e.g., Qdrant) are running. Docker Compose templates will be shipped in `infrastructure/local/compose.yaml`.

### Environment Variables
Create `backend/.env` with at least:
```
POSTGRES_DSN=postgresql+asyncpg://osint:osint@localhost:5432/osint
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
JWT_SECRET=super-secret-string
DEFAULT_PLATFORM_TOKENS={"twitter":"...","linkedin":"..."}
LLM_MODEL=ggml-osint-mistral.bin
```

Create `frontend/.env` with:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_REALTIME_URL=ws://localhost:8000/ws
NEXT_PUBLIC_MAPS_TOKEN=pk.ey...
```

## Starting Services
1. **Backend API & Automation Engine**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   For scheduled jobs and automations:
   ```bash
   celery -A app.worker worker --loglevel=info
   celery -A app.worker beat --loglevel=info
   ```
2. **Crawler Workers**
   ```bash
   cd services/crawler
   python -m crawler.worker --config configs/local.yaml
   ```
3. **Analytics Stream Processor (optional)**
   ```bash
   cd analytics
   poetry run python pipelines/realtime_dashboard.py
   ```
4. **Frontend UI**
   ```bash
   cd frontend
   npm run dev -- --host 0.0.0.0 --port 3000
   ```

## Usage Examples
### 1. Campaign Setup & Monitoring
```bash
# Create a campaign
curl -X POST http://localhost:8000/api/campaigns \
  -H "Content-Type: application/json" \
  -d '{
        "name": "Product Launch",
        "target_keywords": ["brand", "launch"],
        "platforms": ["twitter", "reddit"],
        "objectives": ["lead_generation", "sentiment_tracking"],
        "automation_playbook_id": "pb_leadgen_01"
      }'

# Check campaign status
curl http://localhost:8000/api/campaigns/<campaign_id>/status
```
Monitor KPIs in the UI under **Campaigns → Active Campaigns** to view lead funnels, alert volumes, and sentiment trends.

### 2. Customer & Lead Management
```bash
# Promote a lead to a customer profile via GraphQL mutation
mutation PromoteLead($leadId: ID!) {
  promoteLead(leadId: $leadId) {
    id
    name
    stage
    assignedTo
  }
}
```
Use the UI **CRM Workspace** to segment customers, manage notes, and trigger follow-up sequences.

### 3. Real-Time Dashboards
1. Navigate to **Dashboards → Realtime Overview**.
2. Select campaign filters and time windows; widgets refresh via WebSocket streams (`/ws`).
3. To export aggregated metrics programmatically:
   ```bash
   curl "http://localhost:8000/api/analytics/metrics?campaign_id=<id>&window=1h"
   ```

### 4. Lead Crawling Configuration
- Edit `services/crawler/configs/local.yaml` to specify platforms, rate limits, and field mappings.
- Use the CLI helper to test connector health:
  ```bash
  python -m crawler.cli test-connector twitter --secrets-file ~/.secrets/twitter.yaml
  ```
- Schedule recurring jobs via automation rules:
  ```bash
  curl -X POST http://localhost:8000/api/automations \
    -H "Content-Type: application/json" \
    -d '{
          "name": "Nightly LinkedIn Crawl",
          "trigger": {"type": "cron", "expression": "0 2 * * *"},
          "action": {"type": "run_crawler", "crawler_id": "linkedin_search"}
        }'
  ```

## Troubleshooting
| Symptom | Possible Cause | Resolution |
| --- | --- | --- |
| `ModuleNotFoundError` during backend startup | Virtual environment not activated | Run `pyenv activate osint-manager` (or your venv) before executing commands. |
| `ELIFECYCLE` or `node-gyp` errors during `npm install` | Missing build tools | Install `build-essential` and Python headers: `sudo apt-get install build-essential python3-dev`. |
| Frontend cannot reach backend | Incorrect `NEXT_PUBLIC_API_BASE_URL` or backend port conflict | Verify `.env` values and ensure backend is running on `http://localhost:8000`. |
| Slow LLM responses | Running CPU-only inference | Reduce batch size in `automation_engine.yaml` or deploy GPU-backed inference server. |
| Crawlers blocked by platforms | Aggressive rate limits or IP reputation | Tune rate limits in crawler configs and route traffic through rotating proxies compliant with platform policies. |

## Roadmap
- **Q1** – Deliver MVP with Twitter/Reddit crawlers, campaign automation, and dashboard widgets.
- **Q2** – Expand connector catalog (LinkedIn, Telegram), add multilingual NLP models, and introduce alerting integrations (Slack, Teams).
- **Q3** – Ship advanced analytics (anomaly detection, forecasting), case collaboration tools, and granular RBAC.
- **Q4** – Harden enterprise readiness: SOC2 controls, audit logging, on-prem deployment profiles, and customizable data retention policies.

## Contributing & Support
- Review upcoming work items in `docs/roadmap.md` (to be added) and file issues or pull requests.
- Join the community Slack for implementation discussions and support.
- For security disclosures, email `security@<org>.com` with an encrypted report.

