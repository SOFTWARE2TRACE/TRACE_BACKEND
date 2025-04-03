from fastapi import APIRouter, HTTPException
from models.Project import Project
from services.neo4j_service import create_project_node, get_all_projects, get_project_node # Added get_all_projects
from typing import List, Tuple
from neo4j import GraphDatabase

router = APIRouter()

# In-memory storage for projects (optional backup)
project_db: dict[str, Project] = {}

@router.get("/project")
def get_all_projects_route():
    return get_all_projects()  # Now pulls from Neo4j

@router.post("/project/create")
def create_project(project: Project):
    if project.id in project_db:
        raise HTTPException(status_code=400, detail="Project ID already exists.")
    project_db[project.id] = project
    create_project_node(project)  # Sync to Neo4j
    return {"success": True, "message": f"Project '{project.name}' created."}

@router.get("/project/{project_id}")
def get_project(project_id: str, requester_id: int = 0):  # requester_id is optional
    try:
        project_data = get_project_node(project_id)
        return { "project": project_data }
    except Exception:
        raise HTTPException(status_code=404, detail="Project not found.")
    
@router.put("/project/{project_id}/name")
def update_project_name(project_id: str, new_name: str):
    project = project_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    result = project.set_project_name(new_name)
    return {"success": result}

@router.put("/project/{project_id}/owner")
def set_owner(project_id: str, initials: str, owner_id: str):
    project = project_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    project.set_owner(initials, owner_id)
    return {"success": True}

@router.put("/project/{project_id}/lock")
def lock_project(project_id: str):
    project = project_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    project.lock()
    return {"locked": True}

@router.put("/project/{project_id}/unlock")
def unlock_project(project_id: str):
    project = project_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    project.unlock()
    return {"locked": False}

@router.post("/project/{project_id}/iplist")
def import_ip_list(project_id: str, ip_list: List[Tuple[str, int]]):
    project = project_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    project.import_ip_list(ip_list)
    return {"success": True, "message": "IP list updated."}

@router.get("/project/{project_id}/save")
def save_project(project_id: str):
    project = project_db.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project.save_project()

# this is a test for the neo4J
# uri = "bolt://localhost:7687"
# user = "neo4j"
# password = "12345678"
# driver = GraphDatabase.driver(uri, auth=(user, password))

# @router.get("/neo4j-test")
# def test_neo4j():
#     try:
#         with driver.session() as session:
#             result = session.run("RETURN 'Neo4j connection successful!' AS message")
#             message = result.single()["message"]
#             return {"message": message}
#     except Exception as e:
#         return {"error": str(e)}

