from __future__ import annotations

from collections.abc import Iterable, Sequence

from .models import Campaign, Segment


class ContentAgent:
    def create_campaigns(self, segments: Iterable[Segment]) -> Sequence[Campaign]:
        campaigns: list[Campaign] = []
        for segment in segments:
            for channel in segment.preferred_channels:
                campaigns.append(
                    Campaign(
                        name=f"{segment.name} - {channel} launch",
                        segment=segment.name,
                        channel=channel,
                        message=(
                            f"Solve {segment.pains[0]} with automated research and"
                            " inbound sales workflows."
                        ),
                        call_to_action="Book a tailored demo",
                    )
                )
        return campaigns

    def draft_social_posts(self, campaigns: Iterable[Campaign]) -> list[str]:
        posts: list[str] = []
        for campaign in campaigns:
            posts.append(
                f"[{campaign.channel}] {campaign.message} CTA: {campaign.call_to_action}."
            )
        return posts
