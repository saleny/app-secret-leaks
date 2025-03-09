from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException,status, Path, Response
import uuid
from sqlalchemy.orm import Session
from typing import List  # Важно для аннотаций типов
from app.database import get_db
from app.models import Project, User, ScanResult
from app.schemas.project import ProjectCreate, ProjectOut
from app.schemas.scan import ScanResultOut
from app.utils.gitleaks import scan_repository
from app.dependencies.auth import get_current_user, check_admin

router = APIRouter(tags=["projects"])


@router.post("/", response_model=ProjectOut, status_code=201)
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
        existing_project = db.query(Project).filter(
            Project.repo_url == project.repo_url
        ).first()

        if existing_project:
            raise HTTPException(
                status_code=400,
                detail="Repository already exists"
            )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)

    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Project exists")

    background_tasks.add_task(scan_repository, project_id, project.repo_url)
    return db_project


@router.get("/", response_model=List[ProjectOut])
async def get_projects(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.is_admin:
        projects = db.query(Project).all()
    else:
        projects = db.query(Project).filter(Project.owner_id == current_user.id).all()

    return projects

@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(
    project_id: str = Path(..., regex="^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        (Project.owner_id == current_user.id) | (current_user.is_admin)
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    return project

@router.get("/{project_id}/scans", response_model=List[ScanResultOut])
async def get_scan_results(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверка прав доступа
    project = db.query(Project).filter(
        Project.id == project_id,
        (Project.owner_id == current_user.id) | (current_user.is_admin)
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Получение сканирований
    scans = db.query(ScanResult).filter(
        ScanResult.project_id == project_id
    ).all()

    return scans


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
        project_id: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    # Находим проект и проверяем права
    project = db.query(Project).filter(
        Project.id == project_id,
        (Project.owner_id == current_user.id) | (current_user.is_admin)
    ).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )

    # Удаляем связанные сканирования
    db.query(ScanResult).filter(
        ScanResult.project_id == project_id
    ).delete()

    # Удаляем сам проект
    db.delete(project)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)