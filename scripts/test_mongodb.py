from database.mongodb import MongoDB


def main():
    mongo = MongoDB()

    try:
        db = mongo.connect()

        print("\nMongoDB test successful!")
        print(f"Database: {db.name}")

        print("\nCollections:")
        print(db.list_collection_names())

    finally:
        mongo.close()


if __name__ == "__main__":
    main()