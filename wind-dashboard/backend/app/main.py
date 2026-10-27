from datetime import date, time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.analysis import analyze

app = FastAPI(title="Wind Forecast Dashboard")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Wind Forecast Dashboard API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/api/dashboard")
def dashboard(
    decision_date: date,
    cutoff: time = time(10, 0),
):
    try:
        return analyze(decision_date, cutoff)
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error