from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from config import LLM_PROVIDER, LLM_MODEL, GOOGLE_API_KEY


class LLMFactory:
	"""
	Creates LangChain-compatible language models based on
    application configuration.
	"""

	@staticmethod
	def create() -> BaseChatModel:
		"""
		Creates and returns the language model configured for the application.
		
	    :return: LangChain-compatible chat model.
		"""

		if LLM_PROVIDER == "gemini":

			if not GOOGLE_API_KEY:
				raise ValueError("GOOGLE_API_KEY is not configured.")

			return ChatGoogleGenerativeAI(
				model=LLM_MODEL,
				google_api_key=GOOGLE_API_KEY,
				temperature=0
			)

		raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")

