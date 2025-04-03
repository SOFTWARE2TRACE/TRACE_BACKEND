from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from models import User
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Mock database
users_db = [
    User(id=1, name="Alice", role="analyst", permissions=["SCAN", "VIEW_LOGS"]),
    User(id=2, name="Bob", role="lead_analyst", permissions=["ASSIGN_ANALYST", "REASSIGN_TASK", "MANAGE_PROJECTS"])
]

valid_actions = {"SCAN", "VIEW_LOGS", "ASSIGN_ANALYST", "REASSIGN_TASK", "MANAGE_PROJECTS"}
valid_roles = {"lead_analyst", "analyst"}

# Utility function to find user by ID
def get_user(user_id: int):
    return next((user for user in users_db if user.id == user_id), None)

# Authorization function
@router.post("/authorize_action")
async def authorize_action(user_id: int, action: str):
    user = get_user(user_id)
    if not user or action not in valid_actions:
        logging.warning(f"Authorization failed for user {user_id} with action {action}")
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    authorized = action in user.permissions
    if authorized:
        logging.info(f"User {user_id} authorized for action {action}")
    else:
        logging.warning(f"User {user_id} not authorized for action {action}")

    return {"authorized": authorized}

# Check role permissions
@router.post("/check_role_permissions")
async def check_role_permissions(user_id: int, role: str):
    user = get_user(user_id)
    if not user or role not in valid_roles:
        logging.warning(f"Invalid role check for user {user_id} with role {role}")
        raise HTTPException(status_code=400, detail="Invalid user or role")
    
    logging.info(f"Role permissions checked for user {user_id} with role {role}")
    return {"role": role, "permissions": user.permissions}

# Assign roles function
@router.post("/assign_role")
async def assign_role(user_id: int, role: str):
    user = get_user(user_id)
    if not user or role not in valid_roles:
        logging.warning(f"Role assignment failed for user {user_id} with role {role}")
        raise HTTPException(status_code=400, detail="Invalid user or role")
    
    user.role = role
    user.permissions = [
        "SCAN", "VIEW_LOGS"
    ] if role == "analyst" else [
        "ASSIGN_ANALYST", "REASSIGN_TASK", "MANAGE_PROJECTS"]
    
    logging.info(f"Role {role} assigned to user {user_id}")
    return {"message": "Role assigned", "user": user}

# Change role function
@router.post("/change_role")
async def change_role(user_id: int, new_role: str):
    user = get_user(user_id)
    if not user or new_role not in valid_roles:
        logging.warning(f"Role change failed for user {user_id} to role {new_role}")
        raise HTTPException(status_code=400, detail="Invalid user or role")

    user.role = new_role
    user.permissions = [
        "SCAN", "VIEW_LOGS"
    ] if new_role == "analyst" else [
        "ASSIGN_ANALYST", "REASSIGN_TASK", "MANAGE_PROJECTS"]
    
    logging.info(f"User {user_id} role changed to {new_role}")
    return {"message": "Role changed", "user": user}

# Route restriction dependency
async def check_permissions(user_id: int, action: str):
    user = get_user(user_id)
    if not user or action not in user.permissions:
        logging.warning(f"Access denied: User {user_id} lacks permission for {action}")
        raise HTTPException(status_code=403, detail="Access denied")

# Example route with permission restriction
@router.get("/restricted_data")
async def get_restricted_data(user_id: int, permission_check: bool = Depends(lambda: check_permissions(user_id, "VIEW_LOGS"))):
    return {"message": "Access to restricted data granted"}
