from pydantic import BaseModel
from models.translation_report import TranslationReport


class TranslationRequest(BaseModel):
    """
    Represents a request to process a translation job.
    """
    job_file: str


class TranslationResponse(BaseModel):
    """
    Represents the response returned after processing a translation job.

    Contains the URL of the translated HTML output and the
    corresponding translation report.
    """
    output_url: str
    report: TranslationReport


class HumanReviewRequest(BaseModel):
    """
    Represents a human review submission for a translated segment.
    """
    approved_translation: str