from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.routes import router
from utils.logging_config import setup_logging


# Configure application logging
setup_logging()


app = FastAPI(title="Marketing Asset Translation Engine", version="1.0.0")

# Register API routes
app.include_router(router)

# Serve generated translation outputs
app.mount(
    "/outputs",
    StaticFiles(directory="../data/outputs"),
    name="outputs"
)

@app.get("/health")
def health():
    """
    Returns the health status of the application.
    """
    return {"status": "ok"}