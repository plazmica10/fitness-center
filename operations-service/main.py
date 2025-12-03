from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="Operations Service",
    version="1.0.0",
    description="Microservice 2"
)

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