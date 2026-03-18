from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from .api.v1 import router as api_router
from .config import settings
from .middleware.rate_limit import RateLimitMiddleware
from pathlib import Path

app = FastAPI(title="Blue Plaques API", description="API for Blue Plaques heritage site discovery platform", version="2.0.0")

# Static files
static_dir = Path(__file__).parent.parent / "static"
static_dir.mkdir(exist_ok=True)
frontend_dir = static_dir / "frontend"
if frontend_dir.exists():
    for subdir in ["assets", "images"]:
        d = frontend_dir / subdir
        if d.exists():
            app.mount(f"/{subdir}", StaticFiles(directory=str(d)), name=subdir)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# CORS
allowed_origins = ["*"] if settings.DEBUG else ["https://blueplaques.co.za"]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Rate limiting
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error", "path": str(request.url)})


app.include_router(api_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/{full_path:path}")
async def serve_frontend(request: Request, full_path: str):
    if full_path.startswith("api/"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    frontend_dir = Path(__file__).parent.parent / "static" / "frontend"
    if frontend_dir.exists():
        return FileResponse(frontend_dir / "index.html")
    return {"message": "Blue Plaques API v2.0", "status": "operational"}
