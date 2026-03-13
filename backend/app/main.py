from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .api.v1 import router as api_router
from .config import settings
from .middleware.rate_limit import RateLimitMiddleware

app = FastAPI(
    title="Blue Plaques API",
    description="API for Blue Plaques heritage site discovery platform",
    version="2.0.0"
)

# CORS
allowed_origins = ["*"] if settings.DEBUG else [
    "https://blueplaques.co.za",
    "https://blue-plaques.onrender.com"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "path": str(request.url)}
    )

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Blue Plaques API v2.0", "status": "operational"}

@app.get("/health")
def health():
    return {"status": "healthy"}
