# table creation
import sqlite3


def init_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS workflows (
            run_id TEXT PRIMARY KEY,
            status TEXT,
            inputs TEXT,
            trace TEXT,
            resume_edits_approved INTEGER,
            outreach_approved INTEGER
        )
        """
    )

    conn.commit()
    conn.close()