
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.routes.auth import router as auth_router
from app.database import engine
from app.routes.test_roles import router as test_roles_router

app = FastAPI(
    title="TeluguRead AI API",
    description="Reading Assessment Platform for Telugu and English",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(test_roles_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to TeluguRead AI API",
        "status": "running",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "application": "TeluguRead AI",
    }


@app.get("/api/health/database")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "connected",
            "database": "PostgreSQL",
            "application": "TeluguRead AI",
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed",
        )
