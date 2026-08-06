from models.segment import Segment
from bs4 import BeautifulSoup

class HTMLProcessor:
    """
    Handles extraction and reconstruction of translatable HTML content.
    
    Responsibilities:
    - Parse HTML content
    - Extract translatable text segments
    - Preserve the original HTML structure
    - Rebuild HTML using translated segments
    """
    TRANSLATABLE_BLOCK_TAGS = [
    "title",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p",
    "li",
    "button"]

    def __init__(self):
        """
        Initializes storage for the parsed HTML document and translatable elements.
        """
        self.soup = None
        self.elements = []


    def extract_segments(self, html_content: str) -> list[Segment]:
        """
        Extracts translatable text segments from HTML content.

        :param html_content: Raw HTML content.

        :return: List of extracted Segment objects.
        """
        self.soup = BeautifulSoup(html_content, "html.parser")

        self.elements = self.soup.find_all(self.TRANSLATABLE_BLOCK_TAGS)

        segments = []

        for element in self.elements:
                
            text = element.get_text("", strip=True)
                
            if not text:
                continue


            segment_number = len(segments) + 1
            segment_id = f"seg_{segment_number:03d}"

            segment = Segment(
                segment_id=segment_id,
                source_text=text,
                source_html=str(element)
                )

            segments.append(segment)

        return segments

    

    def rebuild_html(self, translated_segments: list[Segment]) -> str:
        """
        Rebuilds the HTML document using translated segment text.

        Replaces the extracted source text with its corresponding translation 
        while preserving the surrounding HTML structure.
        
        :param translated_segments: Processed segments containing translated text.
        
        :return: The rebuilt HTML document as a string.
        """
        for element, segment in zip(self.elements, translated_segments):

            if segment.translated_text:
                element.string = segment.translated_text

        return str(self.soup)
