from __future__ import annotations

from collections.abc import Sequence

from .chatbot import ChatbotAgent
from .content import ContentAgent
from .crm import CRMSystem
from .models import (
    ChatMessage,
    InboundSalesReport,
    Lead,
    MarketContext,
)
from .research import MarketResearchAgent
from .segmentation import SegmentationAgent


class MarketingOS:
    def __init__(self) -> None:
        self.research_agent = MarketResearchAgent()
        self.segmentation_agent = SegmentationAgent()
        self.content_agent = ContentAgent()
        self.chatbot_agent = ChatbotAgent()
        self.crm = CRMSystem()

    def run_cycle(self, context: MarketContext, messages: Sequence[ChatMessage]) -> InboundSalesReport:
        insights = self.research_agent.analyze(context)
        segments = self.segmentation_agent.build_segments(insights)
        campaigns = self.content_agent.create_campaigns(segments)
        responses = self.chatbot_agent.respond(messages, segments)

        leads = self._qualify_leads(messages, segments)
        self.crm.register_leads(leads)
        self.crm.log_responses(responses)
        appointments = self.crm.schedule_appointments(leads)

        return InboundSalesReport(
            insights=insights,
            segments=segments,
            campaigns=campaigns,
            leads=leads,
            appointments=appointments,
            responses=responses,
        )

    def _qualify_leads(self, messages: Sequence[ChatMessage], segments) -> list[Lead]:
        leads: list[Lead] = []
        segment_name = segments[0].name if segments else "General"
        for message in messages:
            leads.append(
                Lead(
                    lead_id=message.sender,
                    name=message.sender,
                    email=f"{message.sender}@example.com",
                    segment=segment_name,
                    interest="automated inbound sales",
                )
            )
        return leads
