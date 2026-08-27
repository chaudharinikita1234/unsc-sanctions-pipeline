from audit.sync_logger import start_sync_run, complete_sync_run
from database.mongodb import get_database
from src.parser import parse_unsc_xml

def run_pipeline():
    run_id = "UNSC_20260825_001"
    xml_file = "data/raw/unsc_consolidated_list.xml"

    # 1. Start logging in sync_runs collection
    start_sync_run(run_id=run_id, xml_filename="unsc_consolidated_list_2026-08-25.xml")
    
    # 2. Parse XML into MongoDB standard documents
    documents = parse_unsc_xml(xml_file, sync_run_id=run_id)
    total_parsed = len(documents)
    print(f"Successfully parsed {total_parsed} records ready for MongoDB staging!")

    # 3. Stage documents into sanctions_staging collection
    db = get_database()
    if documents:
        db.sanctions_staging.delete_many({})  # Clear previous staging batch
        db.sanctions_staging.insert_many(documents)
        print(f"Inserted {total_parsed} documents into 'sanctions_staging'.")

    # 4. Mark completion with dynamic count
    complete_sync_run(
        run_id=run_id,
        total=total_parsed,
        inserted=total_parsed,  # For initial load, parsed count equals inserted count
        updated=0,
        removed=0,
        unchanged=0
    )

if __name__ == "__main__":
    run_pipeline()