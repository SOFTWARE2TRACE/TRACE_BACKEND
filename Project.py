from fastapi import APIRouter, FastAPI, HTTPException, UploadFile, File, Depends, Query
from pydantic import BaseModel
from backend.services.neo4j_service import create_project_node, create_user_node, link_owner_to_project
import os
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
router = APIRouter()

# Define User and Project models first

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class User(BaseModel):
    id: int
    name: str
    permissions: list[str]  # Permissions like ["MODIFY_PROJECT_OWNER", "IMPORT_PROJECT"]

class Project(BaseModel):
    id: int
    name: str
    owner_id: int
    locked: bool = False

# Mock database
projects_db = {}
users_db = {}

# New Request Model for Creating a Project
class ProjectCreateRequest(BaseModel):
    name: str
    owner_id: int

@app.get("/project")  # ✅ Correct path
def get_all_projects():
    return list(projects_db.values())


# 🔹 New Endpoint: Create a Project
@router.post("/create")
def create_project(request: ProjectCreateRequest):
    new_project_id = max(projects_db.keys(), default=0) + 1
    new_project = Project(id=new_project_id, name=request.name, owner_id=request.owner_id, locked=False)
    
    projects_db[new_project_id] = new_project

    # 💡 Neo4j Sync
    owner_name = users_db.get(request.owner_id, {}).get("name", "Unknown")
    create_user_node(request.owner_id, owner_name)
    create_project_node(new_project)
    link_owner_to_project(request.owner_id, new_project.id)

    return {"message": "Project created successfully", "project_id": new_project_id}

# Helper function to check project existence
def get_project_or_404(project_id: int):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_db[project_id]

# Helper function to check user permissions
def has_permission(user: User, permission: str, project_id: int):
    if permission in user.permissions:
        return True
    raise HTTPException(status_code=403, detail="Permission denied")

# GET project name
@app.get("/projects/{project_id}/name")
def get_project_name(project_id: int):
    project = get_project_or_404(project_id)
    return {"project_name": project.name}

# GET project owner
@app.get("/projects/{project_id}/owner")
def get_project_owner(project_id: int):
    project = get_project_or_404(project_id)
    owner = users_db.get(project.owner_id, {"name": "Unknown"})
    return {"owner": owner}

# GET project ID
@app.get("/projects/{project_id}/id")
def get_project_id(project_id: int):
    project = get_project_or_404(project_id)
    return {"project_id": project.id}

# GET project lock status
@app.get("/projects/{project_id}/locked")
def is_project_locked(project_id: int):
    project = get_project_or_404(project_id)
    return {"locked": project.locked}

# SET project owner
@app.post("/projects/{project_id}/set_owner")
def set_project_owner(project_id: int, new_owner_id: int, requester_id: int):
    project = get_project_or_404(project_id)
    requester = users_db.get(requester_id)
    has_permission(requester, "MODIFY_PROJECT_OWNER", project_id)

    project.owner_id = new_owner_id
    projects_db[project_id] = project  # Ensure update is stored
    return {"message": f"Owner changed to {new_owner_id}"}

# SET project ID
@app.post("/projects/{project_id}/set_id")
def set_project_id(project_id: int, new_id: int, requester_id: int):
    project = get_project_or_404(project_id)
    requester = users_db.get(requester_id)
    has_permission(requester, "MODIFY_PROJECT_ID", project_id)

    if new_id in projects_db:
        raise HTTPException(status_code=400, detail="Project ID already exists")

    # Remove old project and reassign new ID
    projects_db[new_id] = project
    projects_db[new_id].id = new_id
    del projects_db[project_id]  # Remove old project reference

    return {"message": f"Project ID changed to {new_id}"}

# SET project lock
@app.post("/projects/{project_id}/set_lock")
def set_project_lock(project_id: int, lock: bool, requester_id: int):
    project = get_project_or_404(project_id)
    requester = users_db.get(requester_id)
    has_permission(requester, "MODIFY_LOCK", project_id)

    project.locked = lock
    projects_db[project_id] = project  # Ensure update is stored
    return {"message": f"Project lock status changed to {lock}"}

# IMPORT project
@app.post("/projects/import")
def import_project(requester_id: int = Query(..., description="User ID of requester")):
    return {"message": f"Importing project by user {requester_id}"}

# EXPORT project
@app.get("/projects/{project_id}/export")
def export_project(project_id: int, format: str, requester_id: int):
    if format not in ["XML", "CSV"]:
        raise HTTPException(status_code=400, detail="Invalid format")

    project = get_project_or_404(project_id)
    requester = users_db.get(requester_id)
    has_permission(requester, "EXPORT_PROJECT", project_id)

    file_path = f"exports/project_{project_id}.{format.lower()}"
    os.makedirs("exports", exist_ok=True)

    with open(file_path, "w") as file:
        file.write(f"Exported project {project_id} in {format} format.")

    return {"message": "Project exported successfully", "file_path": file_path}
