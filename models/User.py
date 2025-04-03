# models/user_model.py

from pydantic import BaseModel

class UserCreateRequest(BaseModel):
    id: int
    name: str
