import sys
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_optional_user
from app.models import User, UserRole

router = APIRouter(prefix="/api/labs", tags=["labs"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
WEB_LABS_DIR = BASE_DIR / "web-labs"

LAB_DEFINITIONS: dict[str, dict[str, Any]] = {
    "sql-injection": {
        "id": "sql-injection",
        "name": "Web Lab 1: SQL Injection",
        "category": "WEB",
        "port": 8011,
        "script": WEB_LABS_DIR / "sql-injection" / "app" / "main.py",
        "challenge_slug": "lab-sql-injection",
        "description": "Intentionally vulnerable student records query portal. Use SQL injection to union-select the secret flag from admin_secrets.",
        "difficulty": "EASY",
        "points": 150,
    },
    "idor": {
        "id": "idor",
        "name": "Web Lab 2: IDOR / Access Control",
        "category": "WEB",
        "port": 8012,
        "script": WEB_LABS_DIR / "idor" / "app" / "main.py",
        "challenge_slug": "lab-idor",
        "description": "Personnel profile viewer with broken object-level authorization. Fuzz resource identifiers to discover the executive compliance record.",
        "difficulty": "MEDIUM",
        "points": 200,
    },
    "file-upload": {
        "id": "file-upload",
        "name": "Web Lab 3: File Upload",
        "category": "WEB",
        "port": 8013,
        "script": WEB_LABS_DIR / "file-upload" / "app" / "main.py",
        "challenge_slug": "lab-file-upload",
        "description": "Document verification and report uploader. Investigate parser execution and override logic to trigger diagnostic flag output.",
        "difficulty": "MEDIUM",
        "points": 200,
    },
}

# Runtime tracking
RUNNING_PROCS: dict[str, subprocess.Popen] = {}
START_TIMES: dict[str, float] = {}
TIMEOUT_SECONDS = 3600  # 1 hour auto-timeout


def _is_lab_alive(lab_id: str) -> bool:
    proc = RUNNING_PROCS.get(lab_id)
    if proc is None:
        return False
    ret = proc.poll()
    if ret is not None:
        # Process has terminated
        RUNNING_PROCS.pop(lab_id, None)
        START_TIMES.pop(lab_id, None)
        return False
    # Check timeout
    start = START_TIMES.get(lab_id, 0)
    if time.time() - start > TIMEOUT_SECONDS:
        proc.terminate()
        RUNNING_PROCS.pop(lab_id, None)
        START_TIMES.pop(lab_id, None)
        return False
    return True


@router.get("")
def list_labs(user: User | None = Depends(get_optional_user)):
    results = []
    for lab_id, defn in LAB_DEFINITIONS.items():
        alive = _is_lab_alive(lab_id)
        results.append({
            "id": lab_id,
            "name": defn["name"],
            "category": defn["category"],
            "port": defn["port"],
            "target_url": f"http://localhost:{defn['port']}",
            "challenge_slug": defn["challenge_slug"],
            "description": defn["description"],
            "difficulty": defn["difficulty"],
            "points": defn["points"],
            "status": "RUNNING" if alive else "STOPPED",
            "uptime_seconds": int(time.time() - START_TIMES[lab_id]) if alive and lab_id in START_TIMES else 0,
            "timeout_seconds": TIMEOUT_SECONDS,
        })
    return {"items": results}


@router.get("/{lab_id}/status")
def lab_status(lab_id: str, user: User | None = Depends(get_optional_user)):
    defn = LAB_DEFINITIONS.get(lab_id)
    if not defn:
        raise HTTPException(status_code=404, detail="Lab not found")
    alive = _is_lab_alive(lab_id)
    return {
        "id": lab_id,
        "name": defn["name"],
        "status": "RUNNING" if alive else "STOPPED",
        "target_url": f"http://localhost:{defn['port']}",
        "uptime_seconds": int(time.time() - START_TIMES[lab_id]) if alive and lab_id in START_TIMES else 0,
        "timeout_seconds": TIMEOUT_SECONDS,
    }


@router.post("/{lab_id}/start")
def start_lab(lab_id: str, user: User = Depends(get_current_user)):
    defn = LAB_DEFINITIONS.get(lab_id)
    if not defn:
        raise HTTPException(status_code=404, detail="Lab not found")

    if _is_lab_alive(lab_id):
        return {
            "ok": True,
            "message": "Lab is already running",
            "status": "RUNNING",
            "target_url": f"http://localhost:{defn['port']}",
        }

    script_path = defn["script"]
    if not script_path.exists():
        raise HTTPException(status_code=500, detail=f"Lab script not found at {script_path}")

    try:
        proc = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(script_path.parent),
        )
        RUNNING_PROCS[lab_id] = proc
        START_TIMES[lab_id] = time.time()
        # Small grace time for port bind
        time.sleep(0.5)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to start lab process: {exc}")

    return {
        "ok": True,
        "message": f"{defn['name']} started successfully",
        "status": "RUNNING",
        "target_url": f"http://localhost:{defn['port']}",
        "port": defn["port"],
    }


@router.post("/{lab_id}/stop")
def stop_lab(lab_id: str, user: User = Depends(get_current_user)):
    defn = LAB_DEFINITIONS.get(lab_id)
    if not defn:
        raise HTTPException(status_code=404, detail="Lab not found")

    proc = RUNNING_PROCS.get(lab_id)
    if proc:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        RUNNING_PROCS.pop(lab_id, None)
        START_TIMES.pop(lab_id, None)

    return {"ok": True, "message": f"{defn['name']} stopped", "status": "STOPPED"}


@router.post("/{lab_id}/restart")
def restart_lab(lab_id: str, user: User = Depends(get_current_user)):
    stop_lab(lab_id, user)
    time.sleep(0.5)
    return start_lab(lab_id, user)
