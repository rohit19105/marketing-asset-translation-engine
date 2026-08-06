from pydantic import BaseModel

class TranslationJob(BaseModel):
    """
    Represents a validated translation request received from
    an external source such as Jira or Monday.
    """
    job_id: str
    title: str
    source_language: str
    target_language: str
    asset_type: str
    asset_name: str
    requested_by: str
    priority: str
    status: str
    created_at: str