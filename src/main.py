from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from typing import Dict, List
from src.api.search import router as search_router
from src.middleware.rate_limit import RateLimitMiddleware, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

# Initialize rate limiter
rate_limiter = RateLimitMiddleware()

app = FastAPI(
    title="Employee Search API",
    description="A RESTful API for searching employee records",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to enforce rate limiting on all requests.
    """
    # Skip rate limiting for health check and root endpoints
    if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
        response = await call_next(request)
        return response
    
    # Check rate limit
    if rate_limiter.is_rate_limited(request):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Limit: {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds",
            }
        )
    
    # Process the request
    response = await call_next(request)
    
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search_router)

@app.get("/")
async def root():
    """
    Root endpoint to check if the service is running.
    """
    return {
        "message": "Employee Search API is running",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "employee-search-api"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 