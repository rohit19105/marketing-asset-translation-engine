import os
import json
from processors.tm_processor import TMProcessor
from config import OUTPUTS_DIR, TRANSLATION_JOBS_DIR

class HumanReviewService:
    """
    Manages the human-in-the-loop review workflow.

    Handles retrieval of pending reviews, submission of human-approved
    translations, HTML updates, and Translation Memory updates.
    """

    def __init__(self):
        """
        Initializes the human review service.
        """
        self.tm_processor = TMProcessor()

    def get_pending_reviews(self, job_id: str):
        """
        Retrieves pending human reviews for a translation job.

        :param job_id: Identifier of the translation job.

        :return: Job information and segments currently pending human review.
        """
        review_path = os.path.join(OUTPUTS_DIR, job_id, "reviews.json")

        if not os.path.exists(review_path):
            raise FileNotFoundError(f"No reviews found for job {job_id}")


        with open(review_path, "r", encoding="utf-8") as file:
            review_data = json.load(file)

        pending_reviews = []

        for review in review_data["reviews"]:

            if review["status"] == "pending":
                pending_reviews.append(review)

        return {
            "job_id": job_id,
            "pending_reviews": pending_reviews
        }


    def _load_job(self, job_id: str):
        """
        Loads the translation job configuration for a given job ID.

        :param job_id: Identifier of the translation job.

        :return: Translation job data loaded from the job configuration file.  
        """

        jobs_dir = os.path.join(TRANSLATION_JOBS_DIR, f"{job_id}.json")


        for filename in os.listdir(jobs_dir):

            if not filename.endswith(".json"):
                continue

            job_path = os.path.join(jobs_dir, filename)

            with open(job_path, "r", encoding="utf-8") as file:
                job_data = json.load(file)


            if job_data["job_id"] == job_id:
                return job_data

        raise ValueError(f"Translation job {job_id} not found")




    def submit_review(self, job_id: str, segment_id: str, approved_translation: str):
        """
        Processes a human review submission for a translated segment.

        Updates the review status with the approved translation, applies
        the human-approved translation to the translated HTML, and stores
        the approved translation in Translation Memory for future reuse.

        :param job_id: Identifier of the translation job.
        :param segment_id: Identifier of the reviewed segment.
        :param approved_translation: Human-approved translation.
        """
        review_path = os.path.join(OUTPUTS_DIR, job_id, "reviews.json")

        if not os.path.exists(review_path):
            raise FileNotFoundError(f"No pending reviews found for job {job_id}")

        with open(review_path, "r", encoding="utf-8") as file:
            review_data = json.load(file)

        review_found = False

        for review in review_data["reviews"]:

            if review["segment_id"] == segment_id:

                source_text = review["source_text"]
                ai_translation = review["ai_translation"]


                review["approved_translation"] = approved_translation
                review["status"] = "approved"

                review_found = True
                break

        if not review_found:
            raise ValueError(f"Segment {segment_id} not found in reviews")

        self._update_translated_html(
        job_id=job_id,
        ai_translation=ai_translation,
        approved_translation=approved_translation
        )

        with open(review_path, "w", encoding="utf-8") as file:
            json.dump(review_data, file, indent=4, ensure_ascii=False)

        job_data = self._load_job(job_id)

        tm_path = os.path.join(base_path, "data", "translation_memory", "tm.json")

        self.tm_processor.add_entry(
        tm_path=tm_path,
        source_text=source_text,
        translated_text=approved_translation,
        source_language=job_data["source_language"],
        target_language=job_data["target_language"]
        )  

        return review_data


    def _update_translated_html(
        self,
        job_id: str,
        ai_translation: str,
        approved_translation: str,
    ):
        """
        Updates the translated HTML with a human-approved translation.

        Replaces the existing AI-generated translation with the approved
        translation in the output HTML for the specified job.

        :param job_id: Identifier of the translation job.
        :param ai_translation: Existing AI-generated translation.
        :param approved_translation: Human-approved replacement translation.
        """

        output_path = os.path.join(OUTPUTS_DIR, job_id, "translated.html")

        if not os.path.exists(output_path):
            raise FileNotFoundError(
                f"Translated HTML not found for job {job_id}")


        with open(output_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        html_content = html_content.replace(ai_translation, approved_translation, 1)


        with open(output_path, "w", encoding="utf-8") as file:
            file.write(html_content)