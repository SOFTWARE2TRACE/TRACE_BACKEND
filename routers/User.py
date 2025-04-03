from fastapi import APIRouter
from models.User import UserCreateRequest
from services.neo4j_service import get_all_users, create_user_node

router = APIRouter()



@router.get("/users")
def fetch_users():
    return get_all_users()

@router.post("/users/create")
def create_user(user: UserCreateRequest):
    create_user_node(user.id, user.name)
    return {"message": f"User {user.name} (ID: {user.id}) created successfully"}
