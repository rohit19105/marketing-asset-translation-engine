from graph.translation_state import TranslationState
from agents.translation_agent import TranslationAgent


class TranslationGraph:
	"""
	Manages segment translation using the translation agent.

    Coordinates the translation of a segment while passing the required
    source language, target language, and grounding information to the
    translation agent.
	"""

    def __init__(self, translation_agent: TranslationAgent):
        self.translation_agent = translation_agent

#TODO - > check if not used -> delete this