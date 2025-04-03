from fastapi import APIRouter
from models.DbEnumerator import DBEnumerator
from services.neo4j_service import driver  # Adjust if your connection is elsewhere

router = APIRouter()

@router.get("/enumerate-db")
def enumerate_database():
    enumerator = DBEnumerator(driver)
    enumerator.enumerate_database()
    return enumerator.get_summary()
