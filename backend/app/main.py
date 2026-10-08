from fastapi import FastAPI
from backend.app.services.database import check_database_connection
from backend.app.routes.dashboard import router as dashboard_router

app = FastAPI(
    title="Web Server Anomaly Detection API",
    description="Backend API for the Web Server Anomaly Detection System",
    version="1.0.0"
)


app.include_router(dashboard_router)


@app.get("/api/health")
def health_check():
    database_connected = check_database_connection()

    return {
        "status": "ok" if database_connected else "error",
        "database": "connected" if database_connected else "disconnected"
    }