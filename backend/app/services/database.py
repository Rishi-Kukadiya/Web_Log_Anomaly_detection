from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "log_analytics"

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

db = client[DATABASE_NAME]

def check_database_connection():
    try:
        client.admin.command("ping")
        return True
    except Exception:
        return False