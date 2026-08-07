from services.confidence_calculator import ConfidenceCalculator
from processors.glossary_processor import GlossaryProcessor
from graph.quality_review_graph import QualityReviewGraph
from models.translation_report import TranslationReport
from agents.translation_agent import TranslationAgent
from processors.html_processor import HTMLProcessor
from models.translation_job import TranslationJob
from processors.tm_processor import TMProcessor
from agents.quality_agent import QualityAgent
from services.llm_factory import LLMFactory
from models.human_review import HumanReview
from models.segment import Segment
import logging
import json
import os
from config import (
    OUTPUTS_DIR, 
    TRANSLATION_JOBS_DIR,
    ASSETS_DIR,
    GLOSSARY_PATH,
    TM_PATH
    )


logger = logging.getLogger(__name__)

class Workflow:
    """
    Orchestrates the end-to-end marketing asset translation workflow.

    Responsibilities:
    - Load and validate translation jobs
    - Load the marketing asset
    - Extract translatable HTML segments
    - Apply glossary and Translation Memory grounding
    - Perform AI translation and quality evaluation
    - Calculate confidence and route human reviews
    - Rebuild translated HTML
    - Generate and persist translation reports
    - Reuse previously completed job outputs
    """

    def __init__(self):
        """
        Initializes reusable workflow components.
        """

        self.html_processor = HTMLProcessor() # A Workflow has an HTMLProcessor (composition).
        self.glossary_processor = GlossaryProcessor()
        self.tm_processor = TMProcessor()
        
        llm = LLMFactory.create()

        self.translation_agent = TranslationAgent(llm)
        self.quality_agent = QualityAgent(llm)
        self.quality_review_graph = QualityReviewGraph()

        logger.info("Workflow initialized")


    def _get_cached_result(self, job: TranslationJob):
        """
        Returns the cached translation result for a completed job.

        Checks whether both the translated HTML and translation report already
        exist for the given job. If found, loads and returns them to avoid
        reprocessing the job and making unnecessary LLM calls.

        :param job: Translation job to check.

        :return: Tuple containing the output HTML path and TranslationReport 
                 if cached results exist; otherwise None.
        """
        output_dir = os.path.join(OUTPUTS_DIR, job.job_id)

        output_path = os.path.join(output_dir, "translated.html")

        report_path = os.path.join(output_dir, "report.json")


        if not (os.path.exists(output_path) and os.path.exists(report_path)):

            logger.info("job_id=%s | No cached result found", job.job_id)
            return None

        with open(report_path, "r", encoding="utf-8") as file:
            report_data = json.load(file)

        report = TranslationReport(**report_data)


        return output_path, report



    def run(self, job_file: str):
        """
        Executes the end-to-end translation workflow for a translation job.

        Loads the job and source asset, applies glossary and Translation
        Memory grounding, translates and evaluates segments, routes segments
        for human review, rebuilds the HTML, and generates the translation
        report. Reuses cached results when the job was already completed.

        :param job_file: JSON filename present in data/translation_jobs.
        :return: Tuple containing the translated HTML output path and the TranslationReport.
        """
        MAX_SEGMENTS_TO_PROCESS = 7 #Modify For Testing
        
        # 1. Load translation job
        job_path = os.path.join(TRANSLATION_JOBS_DIR, job_file)

        with open(job_path, "r", encoding="utf-8") as file:
            job_data = json.load(file)

            # Converting job_data dict to TranslationJob pydantic object
            job = TranslationJob(**job_data)


        logger.info(
            "Translation job loaded | job_id=%s | asset=%s | target=%s",
            job.job_id,
            job.asset_name,
            job.target_language
        )


        # 2. Check existing result
        cached_result = self._get_cached_result(job)

        if cached_result:
            logger.info("job_id=%s | Cached result found", job.job_id)
            return cached_result


        # 3. Load marketing asset
        asset_path = os.path.join(ASSETS_DIR, job.asset_name)

        with open(asset_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        logger.info("job_id=%s | HTML asset loaded | asset=%s", job.job_id, job.asset_name)


        # 4. Extract text segments
        segments = self.html_processor.extract_segments(html_content)

        logger.info("job_id=%s | Segments extracted | count=%d", job.job_id, len(segments))

        # logger.debug(
        #     "job_id=%s | segment_id=%s | source_text=%s",
        #     job.job_id,
        #     segment.segment_id,
        #     segment.source_text
        # )

        # 5. Load glossary
        glossary_terms = self.glossary_processor.load_glossary(GLOSSARY_PATH)

        logger.info("job_id=%s | Glossary loaded | terms=%d", job.job_id, len(glossary_terms))


        # 6. Load Translation Memory
        tm_entries = self.tm_processor.load_translation_memory(TM_PATH)


        # 7. Enrich Segments
        for segment in segments:

            segment.glossary_matches = (
                self.glossary_processor.find_matches(
                    segment.source_text,
                    glossary_terms
                )
            )

            segment.tm_match = (
                self.tm_processor.find_exact_match(
                    source_text=segment.source_text,
                    source_language=job.source_language,
                    target_language=job.target_language,
                    tm_entries=tm_entries
                )
            )       


        # 8. Process every segment
        translated_segments = []

        for segment in segments[:MAX_SEGMENTS_TO_PROCESS]: # remove

            updated_segment = self._process_segment(segment, job)
            translated_segments.append(updated_segment)

        translated_html = self.html_processor.rebuild_html(translated_segments)
            

        output_dir = os.path.join(OUTPUTS_DIR, job.job_id)

        os.makedirs(output_dir, exist_ok=True)

        # 9. Generate report
        report = self._generate_report(translated_segments, job)

        logger.info("job_id=%s | Translation report generated | %s", job.job_id, report.model_dump())


        # 10. Save report
        report_path = os.path.join(output_dir, "report.json")

        with open(report_path, "w", encoding="utf-8") as file:
            json.dump(report.model_dump(), file, indent=4)

        output_path = os.path.join(output_dir, "translated.html")

        # 11. Save translated html
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(translated_html)


        self._save_human_reviews(translated_segments, job, output_dir)

        return output_path, report



    def _process_segment(self, segment: Segment, job: TranslationJob) -> Segment:
        """
        Processes a single segment through translation and quality evaluation pipeline.

        Uses Translation Memory when available; otherwise invokes the translation agent. 
        The translated segment is then evaluated, assigned a confidence score, and 
        routed for human review if needed.

        :param segment: Segment to process.
        :param job: Translation job containing source and target languages.
        :return: The processed segment with translation and quality metadata.
        """

        # 1. Translation
        if segment.tm_match:

            logger.info("job_id=%s | segment_id=%s | TM HIT", job.job_id, segment.segment_id)

            segment.translated_text = segment.tm_match.translated_text

        else:
            logger.info("job_id=%s | segment_id=%s | AI Translation", job.job_id, segment.segment_id)

            translation_result = self.translation_agent.translate(
                segment=segment,
                source_language=job.source_language,
                target_language=job.target_language
            )

            segment.translated_text = (
                translation_result.translated_text
            )


        # 2. AI Quality Evaluation
        quality_result = self.quality_agent.evaluate(
            segment=segment,
            translated_text=segment.translated_text
            )

        segment.quality_result = quality_result


        # 3. Confidence Calculation
        confidence = ConfidenceCalculator.calculate(quality_result)
        segment.confidence_score = confidence


        # 4. LangGraph - Review Routing
        review_state = self.quality_review_graph.run(segment=segment, confidence_score=confidence)
        segment.requires_human_review = (review_state["requires_human_review"])

        logger.info(
            "job_id=%s | segment_id=%s | confidence=%.2f | human_review=%s",
            job.job_id,
            segment.segment_id,
            segment.confidence_score,
            segment.requires_human_review
        )

        return segment


        # -------------------------------
        # Step 2: Deterministic QA
        # -------------------------------

        # TODO:
        # Check formatting
        # Check DNT terms
        # Check placeholders
        # Check glossary adherence


    def _generate_report(
        self,
        translated_segments: list[Segment],
        job: TranslationJob
    ) -> TranslationReport:
        """
        Generates a summary report for a completed translation job.
        Calculates translation statistics including TM hits, AI translations,
        human reviews, average confidence, and estimated token savings.

        :param translated_segments: Processed translation segments.
        :param job: Translation job associated with the segments.

        :return: TranslationReport containing the job-level translation metrics.
        """

        total_segments = len(translated_segments)
        
        tm_hits = 0

        for segment in translated_segments:

            if segment.tm_match is not None:
                tm_hits += 1

        ai_translations = total_segments - tm_hits


        human_reviews = 0
        
        for segment in translated_segments:

            if segment.requires_human_review:
                human_reviews += 1


        total_confidence = 0
    
        for segment in translated_segments:
            total_confidence += segment.confidence_score

        average_confidence = round(total_confidence/total_segments, 3)
    

        estimated_tokens_saved = tm_hits * 300


        return TranslationReport(
                job_id=job.job_id,
                asset_name=job.asset_name,
                source_language=job.source_language,
                target_language=job.target_language,
                total_segments=total_segments,
                tm_hits=tm_hits,
                ai_translations=ai_translations,
                human_reviews=human_reviews,
                average_confidence=average_confidence,
                estimated_tokens_saved=estimated_tokens_saved
            )


    def _save_human_reviews(
        self, 
        translated_segments: list[Segment],
        job: TranslationJob,
        output_dir: str
    ):
        """
        Saves segments requiring human review for a translation job.
        
        Creates a reviews file containing the source text, AI translation,
        confidence score, review status, and approved translation placeholder
        for each segment routed to human review.

        :param translated_segments: Processed translation segments.
        :param job: Translation job associated with the segments.
        :param output_dir: Directory where the reviews file is stored.

        :return: None
        """

        reviews = []

        for segment in translated_segments:

            if segment.requires_human_review:

                review = HumanReview(
                    segment_id=segment.segment_id,
                    source_text=segment.source_text,
                    ai_translation=segment.translated_text,
                    confidence_score=segment.confidence_score
                )

                reviews.append(review.model_dump())

            if not reviews:
                    return

        review_data = {"job_id": job.job_id, "reviews": reviews}

        review_path = os.path.join(output_dir, "reviews.json")

        with open(review_path, "w", encoding="utf-8") as file:

            json.dump(review_data, file, indent=4, ensure_ascii=False)
