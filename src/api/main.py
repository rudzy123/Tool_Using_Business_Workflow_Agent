from fastapi import FastAPI

from src.api.routes import router as api_router, WORKFLOWS
from src.api.ui import router as ui_router

from src.persistence.migrations import init_db
from src.persistence.repository import WorkflowRepository
from src.agent.job_search_workflow import JobSearchWorkflow

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
        "ui": "/ui/workflow/{run_id}",
    }


@app.on_event("startup")
def startup():
    init_db("workflows.db")

    repo = WorkflowRepository()
    persisted = repo.list_all()

    for wf_state in persisted:
        workflow = JobSearchWorkflow.from_persisted(wf_state)
        WORKFLOWS[workflow.run_id] = workflow

    print(f"[startup] restored {len(WORKFLOWS)} workflows")


app.include_router(api_router)
app.include_router(ui_router)