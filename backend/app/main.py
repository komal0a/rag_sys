from fastapi import FastAPI
from .api.health import router as health_router

app = FastAPI(title="RAG Platform Backend")

app.include_router(health_router, prefix="")

@app.get("/ready")
def ready():
    return {"status": "ready"}
