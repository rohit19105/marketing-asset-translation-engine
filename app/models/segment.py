from models.translation_memory_entry import TranslationMemoryEntry
from models.quality_result import QualityResult
from models.glossary_term import GlossaryTerm
from pydantic import BaseModel, Field
from typing import Optional


class Segment(BaseModel):
	"""
    Represents a translatable unit extracted from a marketing asset.

 	A segment retains its source content and accumulates translation,
    grounding, quality, confidence, and human-review information as it
    moves through the translation workflow.
    """
	segment_id: str
	source_text: str
	source_html: Optional[str] = None
	translated_text: str | None = None

	glossary_matches: list[GlossaryTerm] = Field(default_factory=list)
	tm_match: Optional[TranslationMemoryEntry] = None

	quality_result: QualityResult | None = None
	confidence_score: float | None = None
	requires_human_review: bool = False
	
