from pydantic import BaseModel


class TranslationMemoryEntry(BaseModel):
    """
    Represents a previously translated source-target segment pair
    stored in Translation Memory for future reuse.

    Tracks the source and target languages along with whether the
    translation has been human-approved.
    """
    source_text: str
    translated_text: str
    source_language: str
    target_language: str
    human_approved: bool