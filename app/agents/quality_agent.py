from agents.base_agent import BaseAgent

from models.segment import Segment
from models.quality_result import QualityResult

from prompts.quality_prompt import QUALITY_PROMPT
from utils.glossary_formatter import GlossaryFormatter


class QualityAgent(BaseAgent):
    """
    Evaluates the quality of translated marketing content.
    """

    def evaluate(self, segment: Segment, translated_text: str) -> QualityResult:
        """
        Evaluates a translated segment.

        :param segment: Original source segment.
        :param translated_text: Translation produced by the Translation Agent.
        :return: Quality evaluation.
        """

        glossary_rules = GlossaryFormatter.format(segment.glossary_matches)

        structured_llm = self.llm.with_structured_output(QualityResult)

        chain = QUALITY_PROMPT | structured_llm

        result = chain.invoke(
            {
                "source_text": segment.source_text,
                "translated_text": translated_text,
                "glossary_rules": glossary_rules
            }
        )

        return result