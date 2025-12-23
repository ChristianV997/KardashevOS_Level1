from __future__ import annotations

from datetime import datetime

from .models import ChatMessage, MarketContext
from .orchestrator import MarketingOS


def main() -> None:
    context = MarketContext(
        industry="marketing automation",
        geo="North America",
        products=("AI marketing OS", "inbound sales CRM"),
        competitors=("Competitor A", "Competitor B"),
        goals=("pipeline growth", "higher conversion"),
    )
    messages = [
        ChatMessage(sender="lead-001", content="We need better inbound automation."),
        ChatMessage(sender="lead-002", content="Can you help with segmentation?"),
    ]
    os = MarketingOS()
    report = os.run_cycle(context=context, messages=messages)

    print(report.summary())
    print("\nSample campaigns:")
    for campaign in report.campaigns[:3]:
        print(f"- {campaign.channel}: {campaign.message} ({campaign.call_to_action})")
    print("\nAppointments:")
    for appointment in report.appointments:
        date = appointment.scheduled_for.strftime("%Y-%m-%d %H:%M")
        print(f"- {appointment.lead_id}: {appointment.topic} on {date}")


if __name__ == "__main__":
    main()
