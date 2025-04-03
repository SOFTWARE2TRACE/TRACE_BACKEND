from fastapi import APIRouter, HTTPException
from models import Analyst, Project, Task

router = APIRouter()

# Stub: In-memory data; replace with actual DB queries.
projects_db = [
    Project(id=1, name="Project Alpha"),
    Project(id=2, name="Project Beta")
]

tasks_db = [
    Task(id=101, description="Initial Scan", project_id=1)
]

# Reusing analysts_db from the analysts router for demo purposes
analysts_db = [
    # These would normally be shared or retrieved from a database.
    {"id": 1, "name": "Alice", "assigned_projects": [], "assigned_tasks": []},
    {"id": 2, "name": "Bob", "assigned_projects": [], "assigned_tasks": []}
]

@router.post("/assign_analyst")
async def assign_analyst(project_id: int, analyst_id: int):
    # Stub: Verify project exists (from DB) and assign analyst to project.
    project = next((p for p in projects_db if p.id == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Here you would check permissions via RoleManager before assignment.
    # Update the analyst's assigned projects in the DB.
    return {"message": f"Analyst {analyst_id} assigned to project {project_id}"}

@router.post("/reassign_task")
async def reassign_task(task_id: int, analyst_id: int):
    # Stub: Verify task exists and update assignment in the DB.
    task = next((t for t in tasks_db if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Remove task from any current assignment and assign to new analyst.
    return {"message": f"Task {task_id} reassigned to analyst {analyst_id}"}

@router.post("/create_project")
async def create_project(name: str):
    # Stub: Create a new project in the database.
    return {"message": f"Project '{name}' created (stub)"}

@router.delete("/delete_project")
async def delete_project(project_id: int):
    # Stub: Remove project from the database.
    return {"message": f"Project {project_id} deleted (stub)"}

@router.post("/lock_project")
async def lock_project(project_id: int):
    # Stub: Toggle project lock status in the database.
    return {"message": f"Project {project_id} locked/unlocked (stub)"}
