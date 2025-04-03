from pydantic import BaseModel
from typing import List, Optional, Any, Dict


# User and Role models
class User(BaseModel):
    id: int
    name: str
    role: str  # "analyst" or "lead_analyst"
    permissions: List[str] = []

class Analyst(BaseModel):
    id: int
    name: str
    assigned_projects: List[int] = []
    assigned_tasks: List[int] = []
    active_scans: List[int] = []

class LeadAnalyst(Analyst): # extends Analyst 
    managed_projects: List[int] = []  
    managed_analysts: List[int] = []  

    def assign_analyst(self, project: "Project", analyst: "Analyst") -> bool:
        if project.id in self.managed_projects:  
            if project.id not in analyst.assigned_projects:
                analyst.assigned_projects.append(project.id)
                return True  # success
        return False  # project is not managed or analyst is already assigned

    def reassign_task(self, task: "Task", from_analyst: "Analyst", to_analyst: "Analyst") -> bool:
        if task.id in from_analyst.assigned_tasks:
            from_analyst.assigned_tasks.remove(task.id)
            to_analyst.assigned_tasks.append(task.id)
            return True  # success
        return False  # task not found in from_analyst list


class Project(BaseModel):
    id: int
    name: str

class Task(BaseModel):
    id: int
    description: str
    project_id: int

# Web tree node model for the WebTreeView
class TreeNode(BaseModel):
    id: int
    name: str
    children: Optional[List["TreeNode"]] = []

TreeNode.update_forward_refs()

class RequestModel(BaseModel):
    id: int
    url: str
    method: str = "GET"
    headers: Dict[str, str] = {}
    parameters: Dict[str, str] = {}
    payload: Any = None

