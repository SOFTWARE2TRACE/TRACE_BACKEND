from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analysts, lead_analysts, role_manager, webtree, request_manager, api_endpoints
from routers import Project, ProjectManager, User, DbEnumerator


app = FastAPI()


# Allow CORS for frontend development (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for various subsystems
app.include_router(analysts.router, prefix="/analysts", tags=["analysts"])
app.include_router(lead_analysts.router, prefix="/lead_analysts", tags=["lead_analysts"])
app.include_router(role_manager.router, prefix="/role_manager", tags=["role_manager"])
app.include_router(webtree.router, prefix="/webtree", tags=["webtree"])
# Include the new request manager router
app.include_router(request_manager.router, prefix="/request_manager", tags=["request_manager"])

app.include_router(Project.router)
app.include_router(ProjectManager.router)
app.include_router(User.router)
app.include_router(DbEnumerator.router)

app.include_router(api_endpoints.router)



if __name__ == "__main__":   
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
