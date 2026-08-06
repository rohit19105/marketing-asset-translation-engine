from typing import TypedDict

from models.segment import Segment


class TranslationState(TypedDict):
    """
    Represents the shared state passed between LangGraph nodes.

    Tracks the segment being processed, its confidence score,
    and whether it requires human review.
    """

    segment: Segment
    confidence_score: float | None
    requires_human_review: bool