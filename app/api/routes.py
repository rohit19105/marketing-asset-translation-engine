from fastapi import APIRouter, Request

from api.schemas import TranslationRequest, TranslationResponse
from orchestrator.workflow import Workflow

from api.schemas import HumanReviewRequest
from services.human_review_service import HumanReviewService

import json
import logging

from fastapi import APIRouter, Request, HTTPException
from pydantic import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/translate", response_model=TranslationResponse)
def translate(request_data: TranslationRequest, request: Request):
    """
    Processes a translation job and returns its output URL and report.
    Reuses cached results when the job has already been completed.
    """
    try:
        workflow = Workflow()

        output_path, report = workflow.run(request_data.job_file)

        output_url = (
            f"{str(request.base_url)}"
            f"outputs/{report.job_id}/translated.html"
        )

        return TranslationResponse(output_url=output_url, report=report)

    except FileNotFoundError as error:

        logger.warning("Translation resource not found: %s", error)
        raise HTTPException(status_code=404, detail=str(error))
    
    except json.JSONDecodeError as error:

        logger.warning("Invalid translation job JSON: %s", error)
        raise HTTPException(status_code=400, detail="Translation job contains invalid JSON.")

    except ValidationError as error:

        logger.warning("Invalid translation job schema: %s", error)
        raise HTTPException(status_code=400, detail="Translation job contains invalid or missing fields.")

    except Exception:

        logger.exception("Unexpected error while processing translation job.")
        raise HTTPException(status_code=500, detail="Translation job processing failed.")



@router.get("/reviews/{job_id}")
def get_pending_reviews(job_id: str):
    """
    Retrieves all segments pending human review for a translation job.
    """
    service = HumanReviewService()

    try:
        return service.get_pending_reviews(job_id=job_id)

    except FileNotFoundError as error:

        logger.warning("Reviews not found for job %s: %s", job_id, error)
        raise HTTPException(status_code=404, detail=f"No reviews found for job {job_id}.")

    except Exception:

        logger.exception("Failed to retrieve reviews for job %s", job_id)
        raise HTTPException(status_code=500, detail="Failed to retrieve human reviews.")


@router.post("/reviews/{job_id}/{segment_id}")
def submit_review( job_id: str, segment_id: str, review_request: HumanReviewRequest):
    """
    Submits a human-approved translation for a segment.

    Updates the review status, translated HTML, and Translation Memory
    with the approved translation.
    """
    service = HumanReviewService()

    try:

        result = service.submit_review(
            job_id=job_id,
            segment_id=segment_id,
            approved_translation=review_request.approved_translation
        )

        return {
            "message": "Human review submitted successfully",
            "job_id": job_id,
            "segment_id": segment_id,
            "review": result
        }

    except FileNotFoundError as error:

        logger.warning("Review resource not found: %s", error)
        raise HTTPException(status_code=404, detail=str(error))

    except ValueError as error:

        logger.warning("Invalid human review request: %s", error)
        raise HTTPException(status_code=404, detail=str(error))

    except Exception:

        logger.exception("Human review submission failed | job=%s | segment=%s", job_id, segment_id)
        raise HTTPException(status_code=500, detail="Human review submission failed.")
