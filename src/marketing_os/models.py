from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Sequence


@dataclass(frozen=True)
class MarketInsight:
    topic: str
    trend: str
    pain_points: Sequence[str]
    gains: Sequence[str]
    competitors: Sequence[str]
    target_users: Sequence[str]


@dataclass(frozen=True)
class Segment:
    name: str
    description: str
    pains: Sequence[str]
    gains: Sequence[str]
    preferred_channels: Sequence[str]


@dataclass(frozen=True)
class Campaign:
    name: str
    segment: str
    channel: str
    message: str
    call_to_action: str


@dataclass(frozen=True)
class Lead:
    lead_id: str
    name: str
    email: str
    segment: str
    interest: str


@dataclass(frozen=True)
class Appointment:
    lead_id: str
    scheduled_for: datetime
    topic: str


@dataclass
class CRMRecord:
    lead: Lead
    status: str
    notes: list[str] = field(default_factory=list)
    appointments: list[Appointment] = field(default_factory=list)

    def add_note(self, note: str) -> None:
        self.notes.append(note)

    def schedule(self, appointment: Appointment) -> None:
        self.appointments.append(appointment)


@dataclass(frozen=True)
class ChatMessage:
    sender: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ChatResponse:
    sender: str
    content: str
    in_response_to: ChatMessage


@dataclass(frozen=True)
class InboundSalesReport:
    insights: Sequence[MarketInsight]
    segments: Sequence[Segment]
    campaigns: Sequence[Campaign]
    leads: Sequence[Lead]
    appointments: Sequence[Appointment]
    responses: Sequence[ChatResponse]

    def summary(self) -> str:
        return (
            "Inbound Sales Summary\n"
            f"Insights: {len(self.insights)}\n"
            f"Segments: {len(self.segments)}\n"
            f"Campaigns: {len(self.campaigns)}\n"
            f"Leads: {len(self.leads)}\n"
            f"Appointments: {len(self.appointments)}\n"
            f"Responses: {len(self.responses)}"
        )


@dataclass(frozen=True)
class MarketContext:
    industry: str
    geo: str
    products: Iterable[str]
    competitors: Iterable[str]
    goals: Iterable[str]
