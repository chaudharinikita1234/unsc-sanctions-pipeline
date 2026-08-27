import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure

from config.settings import MONGODB_URI, MONGODB_DATABASE


class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
            # Force a connection test
            self.client.admin.command("ping")
            self.db = self.client[MONGODB_DATABASE]

            print("MongoDB connection successful")
            print(f"Database: {MONGODB_DATABASE}")

            return self.db

        except ConnectionFailure as e:
            print("MongoDB connection failed")
            print(e)
            raise

    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed")


def init_db():
    """Initializes collections, unique indexes, and pipeline validation structure using the MongoDB class."""
    mongo = MongoDB()
    db = mongo.connect()

    try:
        print(f"Initializing '{MONGODB_DATABASE}' database setup...")

        # Collection 1: sanctions
        db.sanctions.create_index([("reference_number", ASCENDING)], unique=True)
        db.sanctions.create_index([("data_id", ASCENDING)])
        db.sanctions.create_index([("record_type", ASCENDING)])
        db.sanctions.create_index([("aliases.alias_name", ASCENDING)])
        print("Created 'sanctions' collection and indexes.")

        # Collection 2: sanctions_staging
        db.sanctions_staging.create_index([("reference_number", ASCENDING)])
        db.sanctions_staging.create_index([("data_id", ASCENDING)])
        print("Created 'sanctions_staging' collection and indexes.")

        # Collection 3: audit_trail
        db.audit_trail.create_index([("reference_number", ASCENDING)])
        db.audit_trail.create_index([("run_id", ASCENDING)])
        db.audit_trail.create_index([("timestamp", DESCENDING)])
        print("Created 'audit_trail' collection and indexes.")

        # Collection 4: sync_runs
        db.sync_runs.create_index([("run_id", ASCENDING)], unique=True)
        db.sync_runs.create_index([("started_at", DESCENDING)])
        print("Created 'sync_runs' collection and indexes.")

        # Initial Log Entry
        sample_run = {
            "run_id": "UNSC_INITIAL_RUN",
            "source": "UNSC_CONSOLIDATED_LIST",
            "source_file": "unsc_consolidated_list.xml",
            "started_at": datetime.datetime.now(datetime.timezone.utc),
            "completed_at": datetime.datetime.now(datetime.timezone.utc),
            "total_records": 0,
            "inserted": 0,
            "updated": 0,
            "removed": 0,
            "unchanged": 0,
            "status": "INITIALIZED",
        }

        db.sync_runs.update_one(
            {"run_id": sample_run["run_id"]},
            {"$setOnInsert": sample_run},
            upsert=True
        )
        print("Logged initial sync status into 'sync_runs'.")
        print("\nInitialization Complete! Existing collections:", db.list_collection_names())

    finally:
        mongo.close()


if __name__ == "__main__":
    init_db()