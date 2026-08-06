from models.glossary_term import GlossaryTerm

class GlossaryFormatter:
    """
    Formats glossary matches into prompt-friendly instructions
    for the translation agent.
    """

    @staticmethod
    def format(glossary_matches: list[GlossaryTerm]) -> str:
        """
        Converts matched glossary terms into structured instructions
        for inclusion in the LLM prompt.

        Do-not-translate terms are explicitly marked to ensure they
        remain unchanged during translation.

        Example:
            AI -> IA
            Celonis -> KEEP UNCHANGED [DNT]

        :param glossary_matches: Glossary terms matched to the source segment.

        :return: Formatted glossary instructions as a string.
        """

        if not glossary_matches:
            return "No glossary rules apply."

        rules = []

        for term in glossary_matches:

            if term.do_not_translate:
                rules.append(
                    f"{term.source_term} -> KEEP UNCHANGED [DNT]"
                )
            else:
                rules.append(
                    f"{term.source_term} -> {term.target_term}"
                )

        return "\n".join(rules)

