# ============================================================
# DESI∞ INFINITY SYSTEM 6.2.0 - PERSISTENT RESEARCH DATABASE
# SQLite Experiment Store with Collision Prevention & Record Preservation
# ============================================================

import sqlite3
import json
from typing import Dict, Any

class ResearchDatabase:
    """
    [CALC] Manages persistent SQLite storage for experiment runs, ensuring 
    historical experiment records are never silently overwritten.
    """
    def __init__(self, db_path: str = "desi_research.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                run_id TEXT PRIMARY KEY,
                timestamp TEXT,
                metrics TEXT
            )
        """)
        conn.commit()
        conn.close()

    def log_experiment(self, run_id: str, timestamp: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check for existing record collision to preserve history
        cursor.execute("SELECT run_id FROM experiments WHERE run_id = ?", (run_id,))
        if cursor.fetchone():
            conn.close()
            raise ValueError(f"Collision error: Experiment run_id '{run_id}' already exists in database. Records are immutable.")

        metrics_json = json.dumps(metrics)
        cursor.execute("INSERT INTO experiments (run_id, timestamp, metrics) VALUES (?, ?, ?)", 
                       (run_id, timestamp, metrics_json))
        conn.commit()
        conn.close()
        return {"run_id": run_id, "status": "EXPERIMENT_LOGGED_SUCCESS"}

if __name__ == "__main__":
    db = ResearchDatabase()
    try:
        print(db.log_experiment("RUN_2026_001", "2026-11-18T12:00:00Z", {"auroc": 0.95}))
    except ValueError as e:
        print("Caught expected collision:", e)

