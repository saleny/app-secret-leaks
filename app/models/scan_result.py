from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"))
    findings = Column(JSON)
    scanned_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String)