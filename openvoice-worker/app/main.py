from fastapi import FastAPI

from app.routes.clone import router as clone_router
from app.routes.health import router as health_router

app = FastAPI(title="openvoice-worker")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "openvoice-worker"}


app.include_router(health_router)
app.include_router(clone_router)
