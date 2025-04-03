from fastapi import APIRouter
from services.state import tree_data

router = APIRouter()

@router.get("/")
def get_tree():
    # Return the current tree nodes from the global tree manager.
    return tree_data
