from typing import TypedDict

from models.segment import Segment


class TranslationState(TypedDict):
    """
    Represents the shared state passed between translation graph nodes.

    Stores the data required as a segment moves through the translation workflow.
    """
    segment: Segment

    source_language: str
    target_language: str

    translation_result: TranslationResult | None

    confidence_score: float | None

    requires_human_review: bool