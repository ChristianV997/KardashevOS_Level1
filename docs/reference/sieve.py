from __future__ import annotations

from typing import Dict, List

from fastapi import APIRouter

from ....schemas.sieve import (
    ClusterItem,
    ClusterRead,
    GeneratedOpportunity,
    SieveClusterRequest,
    SieveClusterResponse,
    SieveGenerateOpportunitiesRequest,
    SieveGenerateOpportunitiesResponse,
    LeadSieveGenerateRequest,
    LeadSieveGenerateResponse,
    LeadSieveGenerated,
)
from ....services.sieve_engine import generate_opportunities_from_clusters, run_sieve
from ....services.lead_sieve_engine import generate_opportunities_from_leads
from ....services.lead_sieve_engine import generate_opportunities_from_leads


router = APIRouter()


@router.post("/cluster", response_model=SieveClusterResponse)
def cluster(req: SieveClusterRequest) -> SieveClusterResponse:
    clusters, items = run_sieve(
        item_type=req.item_type,
        tags_any=req.tags_any,
        limit=req.limit,
        similarity_threshold=req.similarity_threshold,
        min_cluster_size=req.min_cluster_size,
    )

    items_by_id: Dict[int, object] = {it.id: it for it in items}
    out_clusters: List[ClusterRead] = []
    for c in clusters:
        preview: List[ClusterItem] = []
        for iid in c.item_ids[:5]:
            it = items_by_id.get(iid)
            if not it:
                continue
            preview.append(
                ClusterItem(
                    item_id=it.id,
                    title=it.title,
                    source=it.source,
                    url=it.url,
                    summary=it.summary,
                    tags=it.tags or [],
                )
            )
        out_clusters.append(
            ClusterRead(
                cluster_id=c.id,
                label=" / ".join(c.keywords[:3]) or c.id,
                size=len(c.item_ids),
                keywords=c.keywords,
                item_ids=c.item_ids,
                items_preview=preview,
            )
        )

    return SieveClusterResponse(
        item_type=req.item_type,
        threshold=req.similarity_threshold,
        total_items=len(items),
        clusters=out_clusters,
    )


@router.post("/generate_opportunities", response_model=SieveGenerateOpportunitiesResponse)
def generate_opportunities(req: SieveGenerateOpportunitiesRequest) -> SieveGenerateOpportunitiesResponse:
    clusters, items = run_sieve(
        item_type=req.item_type,
        tags_any=req.tags_any,
        limit=req.limit,
        similarity_threshold=req.similarity_threshold,
        min_cluster_size=req.min_cluster_size,
    )
    items_by_id = {it.id: it for it in items}

    created_items = generate_opportunities_from_clusters(
        clusters,
        items_by_id,
        source=req.source,
        base_tags=req.base_tags,
        default_offer_tier=req.default_offer_tier,
    )

    created_payload: List[GeneratedOpportunity] = []
    for it in created_items:
        opp = (it.payload or {}).get("opportunity") if isinstance(it.payload, dict) else None
        niche = "general"
        offer_tier = req.default_offer_tier
        cluster_id = ""
        if isinstance(opp, dict):
            niche = str(opp.get("niche") or niche)
            offer_tier = str(opp.get("offer_tier") or offer_tier)
        sieve = (it.payload or {}).get("sieve") if isinstance(it.payload, dict) else None
        if isinstance(sieve, dict):
            cluster_id = str(sieve.get("cluster_id") or "")
        created_payload.append(
            GeneratedOpportunity(
                opportunity_item_id=it.id,
                gps_score=float(it.gps_score or 0.0),
                title=it.title,
                niche=niche,
                offer_tier=offer_tier,
                cluster_id=cluster_id,
            )
        )

    # crude counters
    skipped_small = 0
    # (clusters returned already filtered by min_cluster_size in engine)

    return SieveGenerateOpportunitiesResponse(
        created=len(created_items),
        created_opportunities=created_payload,
        clusters_considered=len(clusters),
        skipped_small_clusters=skipped_small,
    )


@router.post("/generate_from_leads", response_model=LeadSieveGenerateResponse)
def generate_from_leads(req: LeadSieveGenerateRequest) -> LeadSieveGenerateResponse:
    created = generate_opportunities_from_leads(
        lead_tag=req.lead_tag,
        group_field=req.group_field,
        min_group_size=req.min_group_size,
        source=req.source,
        base_tags=req.base_tags,
        default_offer_tier=req.default_offer_tier,
    )
    payload = [
        LeadSieveGenerated(niche=n, lead_count=0, opportunity_item_id=i, gps_score=s)
        for (n, i, s) in created
    ]
    # lead_count is inside payload.lead_sieve; keep response small.
    return LeadSieveGenerateResponse(
        created=len(payload),
        created_opportunities=payload,
        lead_tag=req.lead_tag,
        group_field=req.group_field,
    )
