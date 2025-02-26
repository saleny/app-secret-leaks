from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
import uuid
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, User
from app.schemas.project import ProjectCreate, ProjectOut
from app.utils.gitleaks import scan_repository
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectOut)
async def create_project(
        project: ProjectCreate,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    project_id = str(uuid.uuid4())
    db_project = Project(
        id=project_id,
        repo_url=project.repo_url,
        project_name=project.repo_url.split("/")[-1].replace(".git", ""),
        owner_id=current_user.id
    )

    try:
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Project exists")

    background_tasks.add_task(scan_repository, project_id, project.repo_url)
    return db_project