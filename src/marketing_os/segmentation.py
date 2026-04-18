from __future__ import annotations

from collections.abc import Iterable, Sequence

from .models import MarketInsight, Segment


class SegmentationAgent:
    def build_segments(self, insights: Iterable[MarketInsight]) -> Sequence[Segment]:
        segments: list[Segment] = []
        for insight in insights:
            segments.append(
                Segment(
                    name=f"{insight.topic} - Growth Teams",
                    description="Revenue teams seeking predictable pipeline and fast activation.",
                    pains=insight.pain_points,
                    gains=insight.gains,
                    preferred_channels=("email", "linkedin", "webinars"),
                )
            )
            segments.append(
                Segment(
                    name=f"{insight.topic} - Operations",
                    description="Operations leaders prioritizing automation and reporting clarity.",
                    pains=(
                        "data silos",
                        "manual workflows",
                        "slow handoffs",
                    ),
                    gains=("automation", "fewer errors", "visibility"),
                    preferred_channels=("slack", "events", "whitepapers"),
                )
            )
        return segments
