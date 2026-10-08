from pymongo import MongoClient

MONGO_URI = "mongodb://172.17.176.1:27017/"
DB_NAME = "web_server_anomaly_detection"

client = MongoClient(MONGO_URI)

# Verify connection
client.admin.command("ping")
print("MongoDB connection successful.")

db = client[DB_NAME]

# Create collections if they do not exist
collections = [
    "traffic_anomalies",
    "error_rate_anomalies",
    "url_access_anomalies",
]

existing = db.list_collection_names()

for collection_name in collections:
    if collection_name not in existing:
        db.create_collection(collection_name)
        print(f"Created collection: {collection_name}")
    else:
        print(f"Collection already exists: {collection_name}")


# Indexes
for collection_name in collections:
    collection = db[collection_name]

    collection.create_index(
        [("ip", 1), ("window_start", 1)],
        name="ip_window_idx"
    )

    collection.create_index(
        [("is_anomaly", 1), ("window_start", -1)],
        name="anomaly_time_idx"
    )


print("\nMongoDB setup completed.")
print(f"Database: {DB_NAME}")

client.close()
