from pydantic import BaseModel
from typing import Optional


class HumanReview(BaseModel):
    """
    Represents a translation segment requiring human review.

    Stores the source text, AI-generated translation, confidence score,
    review status, and the final human-approved translation.
    """

    segment_id: str
    source_text: str
    ai_translation: str
    confidence_score: float

    status: str = "pending"

    approved_translation: Optional[str] = None