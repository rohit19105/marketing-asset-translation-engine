from models.glossary_term import GlossaryTerm
import openpyxl
import re

class GlossaryProcessor:
    """
    Loads and processes approved terminology from the glossary.

    Responsibilities:
    - Load glossary terms from an Excel file.
    - Convert glossary rows into validated GlossaryTerm objects.
    - Find terminology rules relevant to source text.
    """

    def load_glossary(self, glossary_path: str) -> list[GlossaryTerm]:
        """
        Loads and validates glossary terms from an Excel file.

        :param glossary_path: Path to the glossary Excel file.

        :return: List of validated GlossaryTerm objects.
        """
        workbook = openpyxl.load_workbook(
            glossary_path,
            data_only = True
        )

        worksheet = workbook.active

        glossary_terms = []

        for row in worksheet.iter_rows(min_row=2, values_only=True):

            source_term = row[0]
            target_term = row[1]
            dnt_value = row[2]
            notes = row[3]

            if not source_term:
                continue

            do_not_translate = str(dnt_value).strip().upper() == "TRUE"

            glossary_term = GlossaryTerm(
                source_term=str(source_term).strip(),
                target_term=str(target_term).strip(),
                do_not_translate=do_not_translate,
                notes=str(notes).strip() if notes else None
            )

            glossary_terms.append(glossary_term)

        return glossary_terms


    def find_matches(self, text: str, glossary_terms: list[GlossaryTerm]) -> list[GlossaryTerm]:
        """
        Finds glossary terms that occur in the source text.

        Matching is case-insensitive and uses term boundaries
        to reduce false substring matches.

        :param text: Source text to inspect.
        :param glossary_terms: Available glossary terms.

        :return: Glossary terms matched to the source text.
        """

        matches = []

        for term in glossary_terms:

            pattern = rf"\b{re.escape(term.source_term)}\b"

            if re.search(pattern, text, flags=re.IGNORECASE):
                matches.append(term)

        return matches