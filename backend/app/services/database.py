from pymongo import MongoClient

MONGO_URI = "mongodb://172.17.176.1:27017/?directConnection=true"
DATABASE_NAME = "web_server_anomaly_detection"

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