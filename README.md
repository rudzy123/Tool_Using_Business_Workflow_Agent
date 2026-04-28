# Tool‑Using Business Workflow Agent

A production‑shaped, human‑in‑the‑loop workflow agent built with Python and FastAPI.  
This system demonstrates how to orchestrate tool‑using AI workflows with resumable execution, durable persistence, human approvals, and automated tests.

---

## ✨ Key Features

- 🧠 **Tool‑Driven Workflow Execution**
- ✅ **Human‑in‑the‑Loop Approval Gates**
- ♻️ **Resumable & Restart‑Safe Execution**
- 💾 **Durable SQLite Persistence**
- 🔍 **Structured Trace & Run History**
- 🧪 **Approval‑Aware Automated Tests**
- ⚡ **FastAPI Control Plane**
- 🖥️ **Minimal Web UI for Approvals**

This project focuses on **engineering correctness, observability, and control**, not just model outputs.

---

## 🧩 Workflow Overview

The system executes a structured multi‑step workflow:

1. Parse job description
2. Extract required skills (tool‑based)
3. Compare resume to job requirements
4. Generate resume edit suggestions (**approval‑gated**)
5. Generate cover letter bullets
6. Generate outreach draft (**approval‑gated**)
7. Persist final results and execution trace

Human reviewers must explicitly approve high‑risk outputs before the workflow can continue.

---

## 🗺️ Architecture (High Level)

            ┌──────────────────┐
            │   FastAPI API    │
            │  + Web UI        │
            └────────┬─────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │   JobSearchWorkflow      │
        │  (Orchestration Layer)   │
        └───────┬─────────┬────────┘
                │         │
     ┌──────────▼───┐ ┌──▼──────────┐
     │ ApprovalGate │ │ Tool Calls  │
     │ (HITL)       │ │ (Determin.) │
     └───────┬──────┘ └─────┬───────┘
             │              │
             ▼              ▼
    ┌────────────────────────────┐
    │ Persistent Storage         │
    │  • SQLite (workflow state) │
    │  • JSON Traces (runs)      │
    └────────────────────────────┘

## 🔐 Human‑in‑the‑Loop Design

Approval gates are modeled explicitly as **workflow control primitives**, not UI hacks:

- Resume edit suggestions require approval
- Outreach drafts require approval
- Execution pauses deterministically at approval boundaries
- Approval state is persisted and restored across restarts

This mirrors how real enterprise workflow systems handle risk.

---

## 💾 Persistence & Recovery

- Workflow state is persisted to **SQLite**
- Approval decisions are stored explicitly
- On application startup:
  - All workflows are reloaded into memory
  - Approval gates are restored
  - Execution can be resumed safely

This enables **restart‑safe and crash‑resilient workflows**.

---

## 🧪 Testing Strategy

The project includes approval‑aware automated tests that validate:

- Workflow pausing behavior
- Approval unblocking
- Resume correctness
- Persistence accuracy
- Restart‑safe recovery

Tests operate at workflow boundaries and do not depend on UI or API layers.

---

## 🚀 Running the Project

### Setup

bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Run the API
Shell
python -m uvicorn src.api.main:app --reload

Show more lines

API docs: http://localhost:8000/docs
Approval UI: http://localhost:8000/ui/workflow/{run_id}
