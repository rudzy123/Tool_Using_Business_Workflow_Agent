from fastapi import FastAPI
from src.api.routes import router

app = FastAPI(
    title="Job Search Workflow Agent",
    description="Tool-using agent with human-in-the-loop approvals",
    version="0.1.0",
)

app.include_router(router)