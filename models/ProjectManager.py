from pydantic import BaseModel
from typing import List, Tuple, Optional
from datetime import date

class ProjectManager(BaseModel):
    name: str
    owner: str
    IPList: List[Tuple[str, int]]
    dateRange: Optional[Tuple[date, date]] = None
    locked: bool = False