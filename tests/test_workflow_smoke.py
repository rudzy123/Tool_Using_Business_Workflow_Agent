from pathlib import Path

import pytest

from src.agent.job_search_workflow import JobSearchWorkflow


def test_workflow_creates_trace_file(tmp_path, monkeypatch):
    """
    Smoke test to verify:
    - workflow runs end-to-end
    - outputs are returned
    - a trace file is persisted to disk
    """

    # Redirect TraceRecorder to a temporary directory
    def fake_init(self, base_dir=None):
        self.base_dir = Path(tmp_path)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(
        "src.traces.recorder.TraceRecorder.__init__",
        fake_init,
    )

    workflow = JobSearchWorkflow()

    result = workflow.run(
        job_description_text="We are looking for a Python developer.",
        resume_text="Experience with Python and APIs.",
        job_title="Python Developer",
        company_name="TestCorp",
    )

    # --- Assertions on returned structure ---
    assert "metadata" in result
    assert "outreach_draft" in result
    assert result["metadata"].run_id is not None

    # --- Assertions on trace persistence ---
    trace_files = list(tmp_path.glob("run_*.json"))
    assert len(trace_files) == 1


def test_workflow_requires_job_description():
    """
    Negative test to ensure missing required input fails fast.
    """
    workflow = JobSearchWorkflow()

    with pytest.raises(ValueError):
        workflow.run(
            job_description_text="",
            resume_text="Resume text",
            job_title="Title",
            company_name="Company",
        )