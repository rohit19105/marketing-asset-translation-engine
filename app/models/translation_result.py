from pydantic import BaseModel, Field

class TranslationResult(BaseModel):
	"""
	Represents the structured output produced by the translation agent.

	Contains the translated text along with any warnings generated
    during translation.	
    """

	translated_text: str

	warnings: list[str] = Field(default_factory=list)