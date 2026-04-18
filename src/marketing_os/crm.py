from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timedelta

from .models import Appointment, ChatResponse, CRMRecord, Lead


class CRMSystem:
    def __init__(self) -> None:
        self._records: dict[str, CRMRecord] = {}

    def register_leads(self, leads: Iterable[Lead]) -> list[CRMRecord]:
        records: list[CRMRecord] = []
        for lead in leads:
            record = self._records.get(lead.lead_id)
            if record is None:
                record = CRMRecord(lead=lead, status="new")
                self._records[lead.lead_id] = record
            records.append(record)
        return records

    def log_responses(self, responses: Iterable[ChatResponse]) -> None:
        for response in responses:
            lead_id = response.in_response_to.sender
            record = self._records.get(lead_id)
            if record is None:
                continue
            record.add_note(f"Responded: {response.content}")

    def schedule_appointments(self, leads: Iterable[Lead]) -> list[Appointment]:
        appointments: list[Appointment] = []
        for lead in leads:
            appointment = Appointment(
                lead_id=lead.lead_id,
                scheduled_for=datetime.utcnow() + timedelta(days=2),
                topic=f"Discovery for {lead.interest}",
            )
            record = self._records.get(lead.lead_id)
            if record is not None:
                record.schedule(appointment)
                record.status = "scheduled"
            appointments.append(appointment)
        return appointments

    def record_sale(self, lead_id: str, note: str) -> None:
        record = self._records.get(lead_id)
        if record is None:
            return
        record.status = "closed-won"
        record.add_note(note)

    def pipeline_snapshot(self) -> list[CRMRecord]:
        return list(self._records.values())
