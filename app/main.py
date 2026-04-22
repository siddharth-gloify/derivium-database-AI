import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes.query import router as query_router

app = FastAPI(title="fetcherio", docs_url=None, redoc_url=None)

app.include_router(query_router, prefix="/api")

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
# Mount static files last so API routes take precedence
app.mount("/", StaticFiles(directory=os.path.abspath(_STATIC_DIR), html=True), name="static")
