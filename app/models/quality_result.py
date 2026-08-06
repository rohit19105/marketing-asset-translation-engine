from pydantic import BaseModel


class QualityResult(BaseModel):
    """
    Represents the structured quality evaluation produced by the Quality Agent.

    Contains scores for translation accuracy, brand tone, glossary adherence,
    and formatting, along with qualitative feedback.    
    """
    accuracy_score: float
    brand_tone_score: float
    glossary_score: float
    formatting_score: float
    feedback: list[str]