from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.services.database import check_database_connection
from backend.app.routes.dashboard import router as dashboard_router

app = FastAPI(
    title="Web Server Anomaly Detection API",
    description="Backend API for the Web Server Anomaly Detection System",
    version="1.0.0"
)

# Enable CORS for frontend client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)


@app.get("/api/health")
def health_check():
    database_connected = check_database_connection()

    return {
        "status": "ok" if database_connected else "error",
        "database": "connected" if database_connected else "disconnected"
    }