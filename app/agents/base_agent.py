from langchain_core.language_models.chat_models import BaseChatModel

class BaseAgent:
    """
    Base class for AI agents in the translation engine.

    Provides shared LLM access while allowing specialized agents
    to implement their own prompts and business logic.
    """

    def __init__(self, llm: BaseChatModel):
        """
        Initializes the agent with a chat-based language model.

        :param llm: LangChain-compatible chat model.
        """
        self.llm = llm