
from fastapi import FastAPI

from src.api.routes import router as api_router
from src.api.ui import router as ui_router

app = FastAPI(
    title="Job Search Workflow Agent",
    description="Workflow agent with human-in-the-loop approvals",
    version="0.1.0",
)
@app.get("/")
def root():
    return {
        "message": "Job Search Workflow Agent is running",
        "docs": "/docs",
        "ui": "/ui/workflow/{run_id}"
    }

app.include_router(api_router)
app.include_router(ui_router)
