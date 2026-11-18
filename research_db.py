# ============================================================
# DESI∞ INFINITY SYSTEM 6.2.0 - PERSISTENT RESEARCH DATABASE
# Durable SQLite Storage for Experiments, Checkpoints & Provenance
# ============================================================

import sqlite3
import json
from typing import Dict, Any, List

class ResearchDatabase:
    """
    [CALC] Persistent SQLite repository storing experiment fingerprints,
    simulation results, and audit provenance logs securely on disk.
    """
    def __init__(self, db_path: str = "desi_research.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    experiment_name TEXT,
                    system_version TEXT,
                    module_name TEXT,
                    parameters TEXT,
                    outputs TEXT,
                    timestamp_utc TEXT
                )
            """)
            conn.commit()

    def save_experiment(self, record: Dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO experiments 
                (experiment_id, experiment_name, system_version, module_name, parameters, outputs, timestamp_utc)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record["experiment_id"],
                record["experiment_name"],
                record["system_version"],
                record["module_name"],
                json.dumps(record["parameters"]),
                json.dumps(record["outputs"]),
                record["timestamp_utc"]
            ))
            conn.commit()

    def get_experiment(self, experiment_id: str) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM experiments WHERE experiment_id = ?", (experiment_id,))
            row = cursor.fetchone()
            if not row:
                raise KeyError(f"Experiment ID '{experiment_id}' not found in database.")
            return {
                "experiment_id": row[0],
                "experiment_name": row[1],
                "system_version": row[2],
                "module_name": row[3],
                "parameters": json.loads(row[4]),
                "outputs": json.loads(row[5]),
                "timestamp_utc": row[6]
            }

if __name__ == "__main__":
    db = ResearchDatabase("test_desi.db")
    sample_rec = {
        "experiment_id": "exp_abc12345",
        "experiment_name": "Test_Run",
        "system_version": "6.2.0",
        "module_name": "langevin_dynamics",
        "parameters": {"radius": 50.0},
        "outputs": {"displacement": 1.2e-6},
        "timestamp_utc": "2026-11-18T20:00:00Z"
    }
    db.save_experiment(sample_rec)
    print("Retrieved from SQLite DB:", db.get_experiment("exp_abc12345")["experiment_name"])
