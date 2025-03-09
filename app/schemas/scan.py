from pydantic import BaseModel
from datetime import datetime

class ScanResultOut(BaseModel):
    id: str
    project_id: str
    findings: dict  # или конкретная модель для результатов сканирования
    scanned_at: datetime
    status: str

