from __future__ import annotations

from collections.abc import Sequence

from .models import ChatMessage, ChatResponse, Segment


class ChatbotAgent:
    def respond(self, messages: Sequence[ChatMessage], segments: Sequence[Segment]) -> list[ChatResponse]:
        responses: list[ChatResponse] = []
        segment_names = ", ".join(segment.name for segment in segments[:2])
        for message in messages:
            responses.append(
                ChatResponse(
                    sender="MarketingOS",
                    content=(
                        "Thanks for reaching out! We can align you with "
                        f"{segment_names}. Would you like a 20-minute consult?"
                    ),
                    in_response_to=message,
                )
            )
        return responses
