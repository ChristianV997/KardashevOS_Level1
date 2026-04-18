from __future__ import annotations

from collections.abc import Iterable, Sequence

from .models import MarketContext, MarketInsight


class MarketResearchAgent:
    def analyze(self, context: MarketContext) -> Sequence[MarketInsight]:
        insights: list[MarketInsight] = []
        for product in context.products:
            insights.append(
                MarketInsight(
                    topic=f"{context.industry} demand for {product}",
                    trend="steady growth",
                    pain_points=(
                        "slow onboarding",
                        "manual reporting",
                        "unclear ROI",
                    ),
                    gains=("automation", "clear analytics", "faster pipeline"),
                    competitors=tuple(context.competitors),
                    target_users=(
                        f"{context.geo} revenue teams",
                        f"{context.geo} marketing leaders",
                    ),
                )
            )
        return insights

    def summarize_pains(self, insights: Iterable[MarketInsight]) -> list[str]:
        pains: list[str] = []
        for insight in insights:
            pains.extend(insight.pain_points)
        return sorted(set(pains))

    def summarize_gains(self, insights: Iterable[MarketInsight]) -> list[str]:
        gains: list[str] = []
        for insight in insights:
            gains.extend(insight.gains)
        return sorted(set(gains))
