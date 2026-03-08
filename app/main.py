from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.clone import router as clone_router
from app.routes.health import router as health_router

app = FastAPI(title="openvoice-worker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "ok", "service": "openvoice-worker"}


app.include_router(health_router)
app.include_router(clone_router)
