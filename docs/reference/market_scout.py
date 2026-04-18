from __future__ import annotations

from fastapi import APIRouter, Body, Query, HTTPException
from typing import Optional, List

from ....schemas.market_scout import CsvIngestOptions, TextIngestRequest, IngestResult
from ....schemas.research_item import ResearchItemCreate, ResearchItemRead
from ....services.market_scout import ingest_csv_bytes
from ....services.research_registry import research_registry
from ....services.lead_sieve_engine import generate_opportunities_from_leads


router = APIRouter()


@router.post("/ingest/csv", response_model=IngestResult)
async def ingest_csv(
    file: bytes = Body(..., description="CSV content as bytes"),
    source: str = Query("csv_upload"),
    item_type: str = Query("signal", description="signal | lead | note"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to apply to all rows."),
    auto_opps: bool = Query(False, description="If true, auto-generate opportunities from this lead batch."),
    lead_tag: Optional[str] = Query(None, description="Which tag identifies this lead batch for auto_opps."),
    group_field: str = Query("industry", description="Field used to group leads when auto_opps=true"),
    min_group_size: int = Query(5, ge=1, le=500, description="Minimum leads per group to create an opportunity"),
) -> IngestResult:
    """Ingest a CSV payload.

    In environments without the ``python_multipart`` dependency installed we
    accept the CSV content directly in the request body as bytes. Clients
    should send raw CSV data with ``Content-Type: text/csv``.
    """
    # Validate filename by inspecting a synthetic name on tags (not available for bytes)
    # As we cannot inspect a filename, assume the caller sends proper CSV content.
    content = file
    base_tags: List[str] = []
    if tags:
        base_tags = [t.strip() for t in tags.split(",") if t.strip()]
    opts = CsvIngestOptions(source=source, tags=base_tags, item_type=item_type)
    result = ingest_csv_bytes(content, opts)

    # Optional: auto-generate opportunities immediately after ingesting a lead batch.
    if auto_opps and item_type == "lead":
        batch_tag = lead_tag
        if not batch_tag:
            batch_tag = base_tags[0] if base_tags else None
        if batch_tag:
            generate_opportunities_from_leads(
                lead_tag=batch_tag,
                group_field=group_field,
                min_group_size=min_group_size,
                source="lead_sieve",
                base_tags=["auto", "lead_sieve"],
                default_offer_tier="A",
            )

    return result


@router.post("/ingest/text", response_model=ResearchItemRead)
def ingest_text(req: TextIngestRequest) -> ResearchItemRead:
    payload = {"_meta": {"type": req.item_type, "ingest": "text"}, "text": req.text, **(req.extra or {})}
    item = ResearchItemCreate(
        title=req.title,
        source=req.source,
        url=req.url,
        tags=sorted(set(req.tags + ["market_scout", req.item_type])),
        summary=(req.text or "")[:400] if req.text else None,
        payload=payload,
    )
    saved, _ = research_registry.upsert_by_fingerprint(item)
    return saved


@router.get("/recent", response_model=list[ResearchItemRead])
def recent(limit: int = 50) -> list[ResearchItemRead]:
    items = sorted(research_registry.list(limit=10000), key=lambda x: x.created_at, reverse=True)
    return items[: max(1, min(limit, 200))]
