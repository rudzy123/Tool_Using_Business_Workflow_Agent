# save/load/list workflows
import json
import sqlite3
from typing import Optional, List

from src.persistence.models import PersistedWorkflow


class WorkflowRepository:
    def __init__(self, db_path: str = "workflows.db"):
        self.db_path = db_path

    def save(self, wf: PersistedWorkflow) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO workflows
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                wf.run_id,
                wf.status,
                json.dumps(wf.inputs),
                json.dumps(wf.trace),
                int(wf.resume_edits_approved),
                int(wf.outreach_approved),
            ),
        )

        conn.commit()
        conn.close()

    def load(self, run_id: str) -> Optional[PersistedWorkflow]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        row = cursor.execute(
            "SELECT * FROM workflows WHERE run_id = ?",
            (run_id,),
        ).fetchone()

        conn.close()

        if not row:
            return None

        return PersistedWorkflow(
            run_id=row[0],
            status=row[1],
            inputs=json.loads(row[2]),
            trace=json.loads(row[3]),
            resume_edits_approved=bool(row[4]),
            outreach_approved=bool(row[5]),
        )

    def list_all(self) -> List[PersistedWorkflow]:
        """
        Load all persisted workflows (used on app startup).
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        rows = cursor.execute("SELECT * FROM workflows").fetchall()
        conn.close()

        workflows: List[PersistedWorkflow] = []

        for row in rows:
            workflows.append(
                PersistedWorkflow(
                    run_id=row[0],
                    status=row[1],
                    inputs=json.loads(row[2]),
                    trace=json.loads(row[3]),
                    resume_edits_approved=bool(row[4]),
                    outreach_approved=bool(row[5]),
                )
            )

        return workflows