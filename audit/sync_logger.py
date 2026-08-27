import datetime
from database.mongodb import get_database

db = get_database()

def start_sync_run(run_id: str, xml_filename: str):
    """Creates a new tracking record when the pipeline starts."""
    run_doc = {
        "run_id": run_id,
        "source": "UNSC_CONSOLIDATED_LIST",
        "source_file": xml_filename,
        "started_at": datetime.datetime.now(datetime.timezone.utc),
        "completed_at": None,
        "total_records": 0,
        "inserted": 0,
        "updated": 0,
        "removed": 0,
        "unchanged": 0,
        "status": "RUNNING"
    }
    
    db.sync_runs.insert_one(run_doc)
    print(f"Sync Run {run_id} started...")
    return run_id


def complete_sync_run(run_id: str, total: int, inserted: int, updated: int, removed: int, unchanged: int):
    """Updates the tracking record when the pipeline finishes successfully."""
    db.sync_runs.update_one(
        {"run_id": run_id},
        {
            "$set": {
                "completed_at": datetime.datetime.now(datetime.timezone.utc),
                "total_records": total,
                "inserted": inserted,
                "updated": updated,
                "removed": removed,
                "unchanged": unchanged,
                "status": "SUCCESS"
            }
        }
    )
    print(f"Sync Run {run_id} completed successfully!")