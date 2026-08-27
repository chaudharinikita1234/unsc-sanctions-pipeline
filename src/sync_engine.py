from pymongo import MongoClient
from datetime import datetime, timezone
import json

def generate_doc_hash(doc):
    """
    Normalizes and hashes relevant schema fields to check if data changed.
    Excludes system metadata like imported_at.
    """
    clean_doc = {k: v for k, v in doc.items() if k not in ["_id", "metadata"]}
    return json.dumps(clean_doc, sort_keys=True)


def run_delta_sync(mongo_uri, db_name, sync_run_id):
    """
    Compares 'sanctions_staging' against 'sanctions' and applies changes while recording audit history.
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]

    staging_col = db["sanctions_staging"]
    prod_col = db["sanctions"]
    audit_col = db["audit_trail"]

    # Map records by data_id
    staging_map = {doc["data_id"]: doc for doc in staging_col.find({})}
    prod_map = {doc["data_id"]: doc for doc in prod_col.find({})}

    staging_ids = set(staging_map.keys())
    prod_ids = set(prod_map.keys())

    # 1. Detect Changes
    added_ids = staging_ids - prod_ids
    removed_ids = prod_ids - staging_ids
    common_ids = staging_ids & prod_ids

    updated_ids = set()
    for data_id in common_ids:
        if generate_doc_hash(staging_map[data_id]) != generate_doc_hash(prod_map[data_id]):
            updated_ids.add(data_id)

    audit_events = []
    now_utc = datetime.now(timezone.utc).isoformat()

    # 2. Process ADDED Records
    for data_id in added_ids:
        doc = staging_map[data_id]
        doc_copy = {k: v for k, v in doc.items() if k != "_id"}
        prod_col.insert_one(doc_copy)
        
        audit_events.append({
            "sync_run_id": sync_run_id,
            "event_type": "INSERT",
            "data_id": data_id,
            "record_type": doc["record_type"],
            "timestamp": now_utc,
            "new_state": doc_copy
        })

    # 3. Process UPDATED Records
    for data_id in updated_ids:
        old_doc = prod_map[data_id]
        new_doc = staging_map[data_id]
        new_doc_copy = {k: v for k, v in new_doc.items() if k != "_id"}
        
        prod_col.replace_one({"data_id": data_id}, new_doc_copy)

        audit_events.append({
            "sync_run_id": sync_run_id,
            "event_type": "UPDATE",
            "data_id": data_id,
            "record_type": new_doc["record_type"],
            "timestamp": now_utc,
            "previous_state": {k: v for k, v in old_doc.items() if k != "_id"},
            "new_state": new_doc_copy
        })

    # 4. Process REMOVED Records
    for data_id in removed_ids:
        old_doc = prod_map[data_id]
        prod_col.delete_one({"data_id": data_id})

        audit_events.append({
            "sync_run_id": sync_run_id,
            "event_type": "DELETE",
            "data_id": data_id,
            "record_type": old_doc["record_type"],
            "timestamp": now_utc,
            "previous_state": {k: v for k, v in old_doc.items() if k != "_id"}
        })

    # 5. Write to Audit Trail
    if audit_events:
        audit_col.insert_many(audit_events)

    summary = {
        "inserted": len(added_ids),
        "updated": len(updated_ids),
        "deleted": len(removed_ids),
        "total_audit_events": len(audit_events)
    }

    print(f"[Milestone 4] Delta Sync Complete: {summary}")
    return summary