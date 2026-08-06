from prompts.translation_prompt import TRANSLATION_PROMPT
from models.translation_result import TranslationResult
from utils.glossary_formatter import GlossaryFormatter
from agents.base_agent import BaseAgent
from models.segment import Segment


class TranslationAgent(BaseAgent):
    """
    TODO
    Translates grounded marketing segments using an LLM.

    Applies matched glossary constraints and returns structured
    translation output.
    """

    def translate(
            self,
            segment: Segment,
            source_language: str,
            target_language: str
    ) -> TranslationResult:
        """
        Translates a source segment into the requested target language.

        :param segment: Source segment containing glossary grounding.
        :param source_language: Language of the source content.
        :param target_language: Requested target language.

        :return: Structured TranslationResult containing the translated text
                 and any translation warnings.
        """
        glossary_rules = GlossaryFormatter.format(segment.glossary_matches)

        structured_llm = self.llm.with_structured_output(TranslationResult)

        chain = TRANSLATION_PROMPT | structured_llm

        result = chain.invoke(
            {
                "source_language": source_language,
                "target_language": target_language,
                "source_text": segment.source_text,
                "glossary_rules": glossary_rules
            }
        )

        return result


 

