from pymongo import MongoClient, ASCENDING

def initialize_baseline_if_empty(mongo_uri, db_name):
    """
    If production 'sanctions' collection is empty, populate it from 'sanctions_staging'.
    Returns True if baseline was initialized, False if production already exists.
    """
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    staging_col = db["sanctions_staging"]
    prod_col = db["sanctions"]

    # Check if production collection already has data
    if prod_col.count_documents({}) > 0:
        print("[Milestone 3] Production 'sanctions' already initialized. Skipping baseline setup.")
        return False

    # Perform baseline setup
    staging_docs = list(staging_col.find({}, {"_id": 0}))  # Exclude staging _id
    if staging_docs:
        prod_col.insert_many(staging_docs)
        
        # Create Production Indexes
        prod_col.create_index([("data_id", ASCENDING)], unique=True)
        prod_col.create_index([("record_type", ASCENDING)])
        prod_col.create_index([("reference_number", ASCENDING)])

        print(f"[Milestone 3] Baseline Initialized: {len(staging_docs)} records copied to 'sanctions'")
        return True
    
    return False