from models.translation_memory_entry import TranslationMemoryEntry
import os
import json

import logging

logger = logging.getLogger(__name__)

class TMProcessor:
    """
    Handles Translation Memory operations.

    Responsibilities:
    - Load previously stored translations.
    - Find reusable human-approved translations.
    - Add human-approved translations for future reuse.
    """

    def load_translation_memory(
        self,
        tm_path: str
    ) -> list[TranslationMemoryEntry]:
        """
        Loads Translation Memory entries from a JSON file.

        Handles missing, empty, or invalid Translation Memory files
        gracefully by returning an empty list.

        :param tm_path: Path to the Translation Memory JSON file.
        
        :return: List of validated TranslationMemoryEntry objects.
        """

        # TM file does not exist
        if not os.path.exists(tm_path):

            logger.warning("Translation Memory file not found: %s", tm_path)
            return []

        # TM file exists but is empty
        if os.path.getsize(tm_path) == 0:
            
            logger.info("Translation Memory is empty.")       
            return []

        # Load JSON
        try:
    
            with open(tm_path, "r", encoding="utf-8") as file:

                tm_data = json.load(file)

        except json.JSONDecodeError:

            logger.warning(
                "Invalid Translation Memory JSON. "
                "Continuing with empty translation memory."
            )

            return []

        # Convert dictionaries to Pydantic objects
        tm_entries = []

        for entry in tm_data:
            tm_entry = TranslationMemoryEntry(**entry)
            tm_entries.append(tm_entry)


        return tm_entries


    def find_exact_match(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        tm_entries: list[TranslationMemoryEntry]
    ) -> TranslationMemoryEntry | None:
        """
        Finds a human-approved exact match in Translation Memory.

        Matches entries using source text, source language, and target
        language, and only returns translations marked as human-approved.

        :param source_text: Source segment text.
        :param source_language: Language of the source text.
        :param target_language: Requested target language..
        :param tm_entries: Loaded Translation Memory entries.

        :return: Matching TranslationMemoryEntry if found; otherwise None.
        """
        for entry in tm_entries:
            if (
                entry.source_text.strip().lower() == source_text.strip().lower()
                and entry.source_language.lower() == source_language.lower()
                and entry.target_language.lower() == target_language.lower()
                and entry.human_approved
            ):
            
                return entry

        return None


    def add_entry(
            self,
            tm_path: str,
            source_text: str,
            translated_text: str,
            source_language: str,
            target_language: str
    ):
        """
        Adds a human-approved translation to Translation Memory.

        Stores the source-target pair with its language information
        so it can be reused by future translation jobs.        

        :param tm_path: Path to the Translation Memory JSON file.
        :param source_text: Original source text.
        :param translated_text: Human-approved translation.
        :param source_language: Language of the source text.
        :param target_language: Language of the translated text.

        :return: None
        """

        tm_data = []

        if os.path.exists(tm_path):

            try:
                with open(tm_path, "r", encoding="utf-8") as file:
                    tm_data = json.load(file)

            except json.JSONDecodeError:
                tm_data = []

        # Avoid duplicate entries
        for entry in tm_data:

            if (
                entry["source_text"] == source_text
                and entry["source_language"] == source_language
                and entry["target_language"] == target_language
            ):

                # Human feedback should replace the old translation
                entry["translated_text"] = translated_text
                entry["human_approved"] = True

                with open(tm_path, "w", encoding="utf-8") as file:

                    json.dump(tm_data, file, indent=4, ensure_ascii=False)

                return

         # No existing entry → create one
        new_entry = {
            "source_text": source_text,
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language,
            "human_approved": True
        }

        tm_data.append(new_entry)

        with open(tm_path, "w", encoding="utf-8") as file:
            json.dump(tm_data, file, indent=4, ensure_ascii=False)