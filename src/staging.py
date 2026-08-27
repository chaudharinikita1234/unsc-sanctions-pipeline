from pymongo import MongoClient, ASCENDING

def load_to_staging(mongo_uri, db_name, parsed_documents):
    """
    Wipes sanctions_staging and bulk-inserts incoming parsed documents.
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    staging_col = db["sanctions_staging"]

    # 1. Wipe old staging collection for a clean slate
    staging_col.drop()

    # 2. Bulk insert documents
    if parsed_documents:
        result = staging_col.insert_many(parsed_documents)
        print(f"[Milestone 2] Loaded {len(result.inserted_ids)} records into 'sanctions_staging'")

    # 3. Create index on primary key for fast diffing in Milestone 4
    staging_col.create_index([("data_id", ASCENDING)], unique=True)
    staging_col.create_index([("record_type", ASCENDING)])
    
    return staging_col.count_documents({})