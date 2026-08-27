import sys
from datetime import datetime, timezone
from src.parser import parse_unsc_xml
from src.staging import load_to_staging
from src.baseline import initialize_baseline_if_empty
from src.sync_engine import run_delta_sync

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "sanctions_db"
XML_PATH = "data/raw/unsc_consolidated_list_2026-08-25.xml"

def main():
    sync_run_id = f"UNSC_SYNC_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    print(f"Starting pipeline execution: {sync_run_id}")

    # Milestone 1: XML -> Python Dictionaries
    parsed_docs = parse_unsc_xml(XML_PATH, sync_run_id=sync_run_id)
    print(f"[Milestone 1] Parsed {len(parsed_docs)} total documents.")

    # Milestone 2: Dictionaries -> Staging Collection
    load_to_staging(MONGO_URI, DB_NAME, parsed_docs)

    # Milestone 3: Initialize Baseline if production is brand new
    initialized = initialize_baseline_if_empty(MONGO_URI, DB_NAME)

    # Milestone 4: If baseline was already initialized, run Delta Sync
    if not initialized:
        run_delta_sync(MONGO_URI, DB_NAME, sync_run_id)

if __name__ == "__main__":
    main()