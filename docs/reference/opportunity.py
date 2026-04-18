from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class OpportunityFeatures(BaseModel):
    # 0..1 normalized features
    pain: float = Field(ge=0, le=1, description="Pain intensity / urgency (0..1)")
    budget: float = Field(ge=0, le=1, description="Budget / willingness to pay (0..1)")
    reachability: float = Field(ge=0, le=1, description="Ease of reaching buyer (0..1)")
    speed: float = Field(ge=0, le=1, description="Speed to validate (0..1)")
    fulfillment_fit: float = Field(ge=0, le=1, description="Delivery feasibility (0..1)")
    moat: float = Field(ge=0, le=1, description="Compounding advantage (0..1)")
    risk: float = Field(ge=0, le=1, description="Risk (legal/regulatory/chargeback) (0..1)")
    load: float = Field(ge=0, le=1, description="Operational load / complexity (0..1)")


class OpportunityPayload(BaseModel):
    version: str = "v1"
    niche: str = Field(..., description="Target niche (e.g., dental, home-services, realtor)")
    offer_tier: str = Field("A", description="A=Quickstart, B=Retainer, C=SaaS/Subscription")
    name: str = Field(..., description="Short opportunity name")
    problem: str = Field(..., description="The buyer pain in plain language")
    proposed_offer: str = Field(..., description="What we sell / deliver")
    features: OpportunityFeatures
    weights: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional weight overrides (keys: pain,budget,reachability,speed,fulfillment_fit,moat,risk,load)",
    )
    gps_score: Optional[float] = Field(default=None, ge=0, le=1)
    notes: Optional[str] = None
    experiments: List[Dict[str, Any]] = Field(default_factory=list)


class OpportunityCreate(BaseModel):
    title: str
    source: str = "opportunity_engine"
    url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    opportunity: OpportunityPayload


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    opportunity: Optional[OpportunityPayload] = None
    recompute_score: bool = True


class OpportunityScoreRequest(BaseModel):
    features: OpportunityFeatures
    weights: Optional[Dict[str, float]] = None
