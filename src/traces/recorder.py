import json
import os
from pathlib import Path
from typing import Dict, Any


class TraceRecorder:
    """
    Persists workflow run data to disk for observability and inspection.

    Each workflow run is stored as a single JSON file.
    """

    def __init__(self, base_dir: str = "src/traces/runs") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_run(self, run_id: str, payload: Dict[str, Any]) -> None:
        """
        Save a workflow run payload to disk.
        """
        run_path = self.base_dir / f"run_{run_id}.json"
        with open(run_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def load_run(self, run_id: str) -> Dict[str, Any]:
        """
        Load a previously saved workflow run by run_id.
        """
        run_path = self.base_dir / f"run_{run_id}.json"
        if not run_path.exists():
            raise FileNotFoundError(f"No run found for id: {run_id}")

        with open(run_path, "r", encoding="utf-8") as f:
            return json.load(f)