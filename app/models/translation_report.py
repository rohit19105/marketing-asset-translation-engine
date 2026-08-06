from pydantic import BaseModel


class TranslationReport(BaseModel):
    """
    Summarizes the outcome and key metrics of a translation job.

    Includes translation volume, Translation Memory usage, human-review 
    requirements, confidence, and estimated token savings.
    """

    job_id: str
    asset_name: str

    source_language: str
    target_language: str

    total_segments: int
    tm_hits: int
    ai_translations: int
    human_reviews: int

    average_confidence: float
    estimated_tokens_saved: int