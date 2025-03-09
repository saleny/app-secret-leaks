import subprocess
import os
import shutil
from uuid import uuid4
from app.database import SessionLocal
from app.models import ScanResult


def clone_repo(repo_url: str, clone_dir: str) -> bool:
    try:
        subprocess.run(
            ["git", "clone", repo_url, clone_dir],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Clone error: {e.stderr.decode()}")
        return False


def run_gitleaks(clone_dir: str) -> bool:
    try:
        result = subprocess.run(
            ["gitleaks", "detect", "-s", clone_dir, "-r", f"{clone_dir}/report.json"],
            capture_output=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Gitleaks error: {str(e)}")
        return False


def scan_repository(project_id: str, repo_url: str):
    db = SessionLocal()
    try:
        clone_dir = f"/tmp/{project_id}"

        if not clone_repo(repo_url, clone_dir):
            raise Exception("Clone failed")

        if not run_gitleaks(clone_dir):
            raise Exception("Scan failed")

        report_path = os.path.join(clone_dir, "report.json")
        with open(report_path, "r") as f:
            findings = f.read()

        scan_result = ScanResult(
            id=str(uuid4()),
            project_id=project_id,
            findings=findings,
            status="completed"
        )
        db.add(scan_result)
        db.commit()

    except Exception as e:
        scan_result = ScanResult(
            id=str(uuid4()),
            project_id=project_id,
            findings={"error": str(e)},
            status="failed"
        )
        db.add(scan_result)
        db.commit()
    finally:
        shutil.rmtree(clone_dir, ignore_errors=True)
        db.close()