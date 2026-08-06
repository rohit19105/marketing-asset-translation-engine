from pydantic import BaseModel
from typing import Optional


class GlossaryTerm(BaseModel):
    """
    Represents an approved terminology rule used to ground translations
    and maintain terminology consistency.

    Attributes:
        source_term: Term in the source language.
        target_term: Approved term in the target language.
        do_not_translate: Whether the source term must remain unchanged.
        notes: Optional additional guidance for the terminology rule.
    """
    source_term: str
    target_term: str
    do_not_translate: bool
    notes: Optional[str] = None