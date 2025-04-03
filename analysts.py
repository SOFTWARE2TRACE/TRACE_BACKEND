from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from models import Analyst, Project, Task

router = APIRouter()

# Mock database
analysts_db: Dict[int, Analyst] = {
    1: Analyst(id=1, name="Alice", assigned_projects=[], assigned_tasks=[], active_scans=[]),
    2: Analyst(id=2, name="Bob", assigned_projects=[], assigned_tasks=[], active_scans=[])
}

scan_results: Dict[int, str] = {}  # Stores scan results

# Model for new scan request
class ScanRequest(BaseModel):
    analyst_id: int
    project_id: int

# Model for configuring HTTP settings
class HTTPConfig(BaseModel):
    analyst_id: int
    timeout: int
    headers: Dict[str, str]

# Get all analysts
@router.get("/", response_model=List[Analyst])
async def get_analysts():
    return list(analysts_db.values())

# Start a scan for a project
@router.post("/execute_scan")
async def execute_scan(scan_request: ScanRequest):
    if scan_request.analyst_id not in analysts_db:
        raise HTTPException(status_code=404, detail="Analyst not found")

    # Generate a fake scan ID
    new_scan_id = max(scan_results.keys(), default=100) + 1
    #scan_results[new_scan_id] = f"Scan {new_scan_id}: Running for project {scan_request.project_id}"
    scan_results[new_scan_id] = f"Scan {new_scan_id}: Completed - No vulnerabilities found in project {scan_request.project_id}"

    # Assign scan to analyst
    analysts_db[scan_request.analyst_id].active_scans.append(new_scan_id)

    return {"message": "Scan started", "scan_id": new_scan_id}

# Get scan results for an analyst
@router.get("/{analyst_id}/results/")
async def get_scan_results(analyst_id: int):
    if analyst_id not in analysts_db:
        raise HTTPException(status_code=404, detail="Analyst not found")

    active_scans = analysts_db[analyst_id].active_scans
    return {scan_id: scan_results.get(scan_id, "Scan not completed yet") for scan_id in active_scans}

# Configure HTTP settings for an analyst
@router.post("/configure_http/")
async def configure_http(config: HTTPConfig):
    if config.analyst_id not in analysts_db:
        raise HTTPException(status_code=404, detail="Analyst not found")

    return {"message": "HTTP settings configured", "timeout": config.timeout, "headers": config.headers}
