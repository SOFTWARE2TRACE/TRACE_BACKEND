from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import Project, ProjectManager, User
from neo4j_driver import get_driver
from routers import DbEnumerator  
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

 
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(Project.router)
app.include_router(ProjectManager.router)
app.include_router(User.router)
app.include_router(DbEnumerator.router) 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
