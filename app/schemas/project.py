from datetime import datetime
from pydantic import BaseModel

class ProjectCreate(BaseModel):
    repo_url: str

class ProjectOut(BaseModel):
    id: str
    repo_url: str
    project_name: str
    created_at: datetime
    owner_id: int