# KL1 Business Copilot n8n Workflow

This workflow automates the "default money loop" described in the Business Copilot docs: ingest signals/leads, cluster them into Opportunities, generate outbound campaigns, and log outcomes so experiments can be adapted over time.【F:docs/reference/BUSINESS_COPILOT.md†L32-L44】 The steps align with the KL1/VimuttiOS integrated architecture that treats each stack as a module orchestrated through shared services.【F:docs/reference/ARCHITECTURE.md†L1-L23】 The agent mesh that oversees research, architecture, business sieve, and growth ops is preserved as context for how this loop fits into the broader OS.【F:docs/reference/kl1_agents.yaml†L1-L41】

## Workflow nodes

The exported n8n workflow lives at `workflows/kl1_business_copilot_n8n.json` and includes these stages:

1. **Manual Trigger** – start the loop on-demand.
2. **Set Base Vars** – captures the Business Copilot API URL, lead tag, and personalization defaults.
3. **Prep Lead CSV** – provides a starter CSV payload of demo leads for MarketScout ingestion.
4. **Ingest Leads (CSV)** – posts the CSV to `/api/v1/market_scout/ingest/csv`, tagging the batch and enabling auto-opportunity generation for lead groups.
5. **Generate Opportunities** – calls `/api/v1/sieve/generate_from_leads` to cluster the tagged leads into opportunities with GPS scoring ready for outbound use.【F:docs/reference/sieve.py†L54-L98】
6. **Generate Outbound** – sends the top opportunity to `/api/v1/outbound/generate` so the outbound engine builds a campaign and linked experiment.【F:docs/reference/outbound_schema.py†L9-L48】
7. **Approve Campaign** – confirms the draft so it can be exported/logged.【F:docs/reference/outbound_endpoint.py†L70-L96】
8. **Log Metrics** – posts basic outcome metrics to `/api/v1/outbound/campaigns/{id}/log`, which updates the linked experiment and optionally marks it complete.【F:docs/reference/outbound_endpoint.py†L97-L139】

## Import and run

1. Start the Business Copilot FastAPI service locally (see `integration/docker-compose.business_copilot.yml` in the v7 bundle) so the API is available at `http://127.0.0.1:8000`.
2. In n8n, import `workflows/kl1_business_copilot_n8n.json` via **Workflows → Import from File**.
3. Adjust the `Set Base Vars` node to point `baseUrl` to your deployment and to set your preferred lead tag, calendar link, and tags.
4. Run the workflow. After it completes, check the Business Copilot API:
   - `GET /api/v1/market_scout/recent` should show the ingested lead batch.【F:docs/reference/market_scout.py†L38-L52】
   - `GET /api/v1/outbound/campaigns` should show the generated, approved campaign ready for CSV export and further iteration.【F:docs/reference/outbound_endpoint.py†L33-L69】

Use the resulting experiment metrics to decide whether to adapt the offer or run another variant, consistent with the iterative GPS score loop outlined in the Business Copilot docs.【F:docs/reference/BUSINESS_COPILOT.md†L12-L31】
