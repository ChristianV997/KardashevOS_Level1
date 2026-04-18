from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OutboundGenerateRequest(BaseModel):
    """Generate outbound sequences for a set of leads.

    This is intentionally template-driven (no external LLM dependency) so the pilot is runnable.
    You can later replace the template renderer with an LLM-backed renderer.
    """

    opportunity_id: int = Field(..., ge=1)
    lead_ids: Optional[List[int]] = None
    lead_tag: Optional[str] = None

    channel: str = Field("email", description="email|sms|dm")
    language: str = Field("en", description="en|es")
    sequence_steps: int = Field(3, ge=1, le=5)
    variant: str = Field("v1", description="Experiment variant label")

    sender_name: Optional[str] = None
    agency_name: Optional[str] = None
    calendar_link: Optional[str] = None
    personalization: str = Field("med", description="low|med|high")

    auto_create_experiment: bool = True
    store_as_research_item: bool = True


class OutboundGenerateResponse(BaseModel):
    campaign_id: int
    experiment_id: Optional[int] = None
    lead_count: int
    channel: str
    language: str
    variant: str
    preview: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Small preview of generated content (first few leads).",
    )


class OutboundCampaignOut(BaseModel):
    id: int
    opportunity_id: int
    name: str
    channel: str
    language: str
    variant: str
    status: str = "draft"
    approved_at: Optional[str] = None
    lead_ids: List[int]
    experiment_id: Optional[int] = None


class OutboundGenerateABRequest(BaseModel):
    """Generate two variants (A/B) for the same lead batch."""

    opportunity_id: int = Field(..., ge=1)
    lead_ids: Optional[List[int]] = None
    lead_tag: Optional[str] = None

    channel: str = Field("email", description="email|sms|dm")
    language: str = Field("en", description="en|es")
    sequence_steps: int = Field(3, ge=1, le=5)

    variant_a: str = Field("A")
    variant_b: str = Field("B")

    sender_name: Optional[str] = None
    agency_name: Optional[str] = None
    calendar_link: Optional[str] = None

    auto_create_experiment: bool = True


class OutboundGenerateABResponse(BaseModel):
    campaign_id_a: int
    campaign_id_b: int
    experiment_id_a: Optional[int] = None
    experiment_id_b: Optional[int] = None
    lead_count: int
    channel: str
    language: str
    preview_a: List[Dict[str, Any]] = Field(default_factory=list)
    preview_b: List[Dict[str, Any]] = Field(default_factory=list)


class OutboundApproveResponse(BaseModel):
    campaign_id: int
    status: str
    approved_at: Optional[str] = None


class OutboundLogMetricsRequest(BaseModel):
    """Convenience endpoint to update linked experiment metrics."""

    outreaches: Optional[int] = None
    replies: Optional[int] = None
    booked_calls: Optional[int] = None
    closes: Optional[int] = None
    revenue_usd: Optional[float] = None
    cost_usd: Optional[float] = None
    mark_complete: bool = False
