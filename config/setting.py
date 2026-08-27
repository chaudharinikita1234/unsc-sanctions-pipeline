import os
from dotenv import load_dotenv


load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not configured")

if not MONGODB_DATABASE:
    raise ValueError("MONGODB_DATABASE is not configured")