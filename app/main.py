import os
import time

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import Request

from app.logger import get_logger, setup_logging
from app.api.routes.query import router as query_router
from app.api.routes.v1_query import router as v1_query_router

setup_logging()
log = get_logger(__name__)

app = FastAPI(title="fetcherio", docs_url=None, redoc_url=None)


@app.middleware("http")
async def _log_requests(request: Request, call_next):
    t0 = time.perf_counter()
    log.debug("→ %s %s", request.method, request.url.path)
    response = await call_next(request)
    elapsed = time.perf_counter() - t0
    log.info("← %s %s %d (%.3fs)", request.method, request.url.path, response.status_code, elapsed)
    return response


@app.exception_handler(RequestValidationError)
async def _validation_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api/v1/"):
        log.warning("v1/query | bad request | path=%s | detail=%s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=400,
            content={"status": "error", "code": "BAD_REQUEST", "message": "Malformed JSON or missing required field."},
        )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


app.include_router(query_router, prefix="/api")
app.include_router(v1_query_router, prefix="/api")

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
# Mount static files last so API routes take precedence
app.mount("/", StaticFiles(directory=os.path.abspath(_STATIC_DIR), html=True), name="static")
