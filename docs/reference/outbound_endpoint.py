from __future__ import annotations

import csv
import io
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ....schemas.outbound import (
    OutboundGenerateRequest,
    OutboundGenerateResponse,
    OutboundGenerateABRequest,
    OutboundGenerateABResponse,
    OutboundCampaignOut,
    OutboundLogMetricsRequest,
    OutboundApproveResponse,
)
from ....services.outbound_engine import generate_campaign
from ....services.outbound_registry import outbound_registry
from ....services.experiment_registry import experiment_registry
from ....schemas.experiment import ExperimentUpdate

router = APIRouter()


@router.post("/generate", response_model=OutboundGenerateResponse)
def generate(req: OutboundGenerateRequest) -> OutboundGenerateResponse:
    try:
        campaign, exp_id = generate_campaign(req)
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))
    # small preview (first 3 leads)
    preview = []
    for d in campaign.drafts[:3]:
        first = d.messages[0] if d.messages else None
        preview.append(
            {
                "lead_id": d.lead_id,
                "company": d.lead.get("company") or d.lead.get("business"),
                "subject": getattr(first, "subject", None),
                "body": getattr(first, "body", "")[:240],
            }
        )
    return OutboundGenerateResponse(
        campaign_id=campaign.id,
        experiment_id=exp_id,
        lead_count=len(campaign.lead_ids),
        channel=campaign.channel,
        language=campaign.language,
        variant=campaign.variant,
        preview=preview,
    )


@router.get("/campaigns", response_model=List[OutboundCampaignOut])
def list_campaigns(opportunity_id: Optional[int] = None, limit: int = 50) -> List[OutboundCampaignOut]:
    camps = outbound_registry.list(opportunity_id=opportunity_id, limit=limit)
    return [
        OutboundCampaignOut(
            id=c.id,
            opportunity_id=c.opportunity_id,
            name=c.name,
            channel=c.channel,
            language=c.language,
            variant=c.variant,
            status=getattr(c, "status", "draft"),
            approved_at=(c.approved_at.isoformat() if getattr(c, "approved_at", None) else None),
            lead_ids=c.lead_ids,
            experiment_id=c.experiment_id,
        )
        for c in camps
    ]


@router.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: int) -> Dict[str, Any]:
    camp = outbound_registry.get(campaign_id)
    if not camp:
        raise HTTPException(status_code=404, detail="campaign not found")
    return camp.model_dump()


@router.get("/campaigns/{campaign_id}/export/csv")
def export_csv(campaign_id: int) -> Response:
    camp = outbound_registry.get(campaign_id)
    if not camp:
        raise HTTPException(status_code=404, detail="campaign not found")

    # Safety: default export requires approval.
    if getattr(camp, "status", "draft") != "approved":
        raise HTTPException(status_code=409, detail="campaign is not approved; call /approve first")

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["lead_id", "step", "channel", "subject", "message"])
    for d in camp.drafts:
        for m in d.messages:
            writer.writerow([
                d.lead_id,
                m.step_index,
                m.channel,
                m.subject or "",
                m.body,
            ])
    data = buf.getvalue().encode("utf-8")
    filename = f"outbound_campaign_{campaign_id}.csv"
    return Response(
        content=data,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/generate_ab", response_model=OutboundGenerateABResponse)
def generate_ab(req: OutboundGenerateABRequest) -> OutboundGenerateABResponse:
    # Generate two campaigns with light subject/body hooks to encourage real A/B testing.
    req_a = OutboundGenerateRequest(**{**req.model_dump(), "variant": req.variant_a})
    req_b = OutboundGenerateRequest(**{**req.model_dump(), "variant": req.variant_b})
    camp_a, exp_a = generate_campaign(req_a)
    camp_b, exp_b = generate_campaign(req_b)

    def _preview(camp):
        out = []
        for d in camp.drafts[:3]:
            first = d.messages[0] if d.messages else None
            out.append(
                {
                    "lead_id": d.lead_id,
                    "company": d.lead.get("company") or d.lead.get("business"),
                    "subject": getattr(first, "subject", None),
                    "body": getattr(first, "body", "")[:240],
                }
            )
        return out

    return OutboundGenerateABResponse(
        campaign_id_a=camp_a.id,
        campaign_id_b=camp_b.id,
        experiment_id_a=exp_a,
        experiment_id_b=exp_b,
        lead_count=len(camp_a.lead_ids),
        channel=camp_a.channel,
        language=camp_a.language,
        preview_a=_preview(camp_a),
        preview_b=_preview(camp_b),
    )


@router.post("/campaigns/{campaign_id}/approve", response_model=OutboundApproveResponse)
def approve(campaign_id: int) -> OutboundApproveResponse:
    camp = outbound_registry.get(campaign_id)
    if not camp:
        raise HTTPException(status_code=404, detail="campaign not found")
    if getattr(camp, "status", "draft") == "approved":
        return OutboundApproveResponse(
            campaign_id=camp.id,
            status="approved",
            approved_at=camp.approved_at.isoformat() if camp.approved_at else None,
        )
    from datetime import datetime

    camp = camp.model_copy(update={"status": "approved", "approved_at": datetime.utcnow()})
    outbound_registry.update(campaign_id, camp)
    return OutboundApproveResponse(
        campaign_id=camp.id,
        status=camp.status,
        approved_at=camp.approved_at.isoformat() if camp.approved_at else None,
    )


@router.post("/campaigns/{campaign_id}/log")
def log_metrics(campaign_id: int, req: OutboundLogMetricsRequest) -> Dict[str, Any]:
    camp = outbound_registry.get(campaign_id)
    if not camp:
        raise HTTPException(status_code=404, detail="campaign not found")
    if not camp.experiment_id:
        raise HTTPException(status_code=400, detail="campaign has no linked experiment")
    exp = experiment_registry.get(camp.experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="linked experiment not found")

    metrics = dict(exp.metrics or {})
    for k, v in {
        "outreaches": req.outreaches,
        "replies": req.replies,
        "booked_calls": req.booked_calls,
        "closes": req.closes,
        "revenue_usd": req.revenue_usd,
    }.items():
        if v is not None:
            metrics[k] = v

    upd = {
        "metrics": metrics,
    }
    if req.cost_usd is not None:
        upd["cost_usd"] = float(req.cost_usd)

    updated = experiment_registry.update(exp.id, ExperimentUpdate(**upd))
    if not updated:
        raise HTTPException(status_code=500, detail="failed to update experiment")

    result = {"experiment_id": updated.id, "metrics": updated.metrics}

    if req.mark_complete:
        # reuse the existing experiments endpoint behavior by calling the engine through HTTP is overkill;
        # we simply set status here, and user can call /experiments/{id}/complete for adaptation.
        updated2 = experiment_registry.update(exp.id, ExperimentUpdate(status="completed"))
        result["status"] = updated2.status if updated2 else "completed"

    return result
