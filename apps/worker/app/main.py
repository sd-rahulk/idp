import asyncio
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException
from .core.config import get_settings
from .orchestration.runner import run_scan

app = FastAPI(title="AegisFlow Worker", version="0.1.0")


def check_secret(authorization: str | None) -> None:
    expected = get_settings().worker_auth_secret
    if expected and authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="Invalid worker credential")


@app.get("/health")
def health() -> dict:
    return {"service": "aegisflow-worker", "status": "ok"}


@app.post("/internal/scans/{scan_id}/run", status_code=202)
def start_scan(scan_id: str, background_tasks: BackgroundTasks, authorization: str | None = Header(default=None)) -> dict:
    check_secret(authorization)
    background_tasks.add_task(run_scan, scan_id)
    return {"accepted": True, "scan_id": scan_id}
