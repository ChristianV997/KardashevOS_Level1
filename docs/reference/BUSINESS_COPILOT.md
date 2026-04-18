# KL1 Business Copilot (Money Ops Pilot)

This adds a **Business Copilot** service to your KL1/VimuttiOS bundle:

- **Opportunity Engine** (rank & manage money opportunities)
- **MarketScout ingestion** (CSV/text signals & leads, with de-duplication)
- **Experiment Runner** (log outcomes, trigger adaptation, update GPS score)
- **Outbound Kit** (generate sequences + export CSV + log results)

Everything is exposed via a FastAPI API with OpenAPI docs.

## Quickstart (Docker)

```bash
cd integration
mkdir -p runtime/business_copilot
docker compose -f docker-compose.business_copilot.yml up --build
```

Open:
- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

Data persistence:
- `integration/runtime/business_copilot/research_items.json`
- `integration/runtime/business_copilot/experiments.json`
- `integration/runtime/business_copilot/outbound_campaigns.json`

## Local run (no docker)

```bash
cd services/business_copilot/kl1_meta_backend
PYTHONPATH=. uvicorn kl1_meta_backend.app.main:app --reload
```

## Default money loop

1) **Ingest** signals/leads (MarketScout)
2) Turn top clusters into **Opportunities** (Opportunity Engine)
3) Run **Outbound** campaigns (Outbound Kit) and log metrics
4) **Complete** experiments to adapt features + recompute `gps_score`

## Endpoints

- Opportunities
  - `POST /api/v1/opportunities/`
  - `GET /api/v1/opportunities/`
  - `POST /api/v1/opportunities/{id}/score`

- MarketScout
  - `POST /api/v1/market_scout/ingest/csv`
  - `POST /api/v1/market_scout/ingest/text`

- Experiments
  - `POST /api/v1/experiments/`
  - `POST /api/v1/experiments/{id}/complete`

- Sieve (auto-discovery)
  - `POST /api/v1/sieve/cluster`
  - `POST /api/v1/sieve/generate_opportunities`

- Outbound
  - `POST /api/v1/outbound/generate`
  - `GET /api/v1/outbound/campaigns/{id}/export/csv`
  - `POST /api/v1/outbound/campaigns/{id}/log`

- Evals (smoke)
  - `GET /api/v1/evals/run`

## Recommended workflow

Start with one niche + one offer:
- Dental/medspa/home-services: missed-call recovery + booking follow-ups

Use the OS as a lab:
- One campaign → log outcomes → adapt → raise GPS on winners → repeat.
