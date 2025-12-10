from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import db
from routers.rooms import router as rooms_router
from routers.payments import router as payments_router
from routers.trainers import router as trainers_router
from routers.classes import router as classes_router
from routers.attendances import router as attendances_router
from routers.queries import router as queries_router
from routers.analytics import router as analytics_router

app = FastAPI(
    title="Operations Service",
    version="1.0.0",
    description="Fitness Center Operations Microservice - Protected by JWT Authentication"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rooms_router)
app.include_router(payments_router)
app.include_router(trainers_router)
app.include_router(classes_router)
app.include_router(attendances_router)
app.include_router(queries_router)
app.include_router(analytics_router)

@app.on_event("startup")
def on_startup():
    # ensure ClickHouse tables exist
    try:
        db.init_tables()
    except Exception:
        # don't crash startup; errors will show in logs
        pass

@app.get("/")
def root():
    return {"message": "Operations Service is running!"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )