from pydantic import BaseModel, Field
from typing import List, Tuple, Optional

class Project(BaseModel):
    name: str
    id: str
    owner: str  # Owner initials
    isLocked: bool = False
    files: List[str] = Field(default_factory=list)
    IPList: List[Tuple[str, int]] = Field(default_factory=list)

    def set_project_name(self, new_name: str) -> bool:
        if new_name:
            self.name = new_name
            return True
        return False

    def set_owner(self, owner_initials: str, owner_id: str):
        self.owner = owner_initials + ":" + owner_id

    def lock(self):
        self.isLocked = True

    def unlock(self):
        self.isLocked = False

    def import_ip_list(self, ip_list: List[Tuple[str, int]]):
        self.IPList = ip_list

    def save_project(self) -> dict:
        return self.dict()
