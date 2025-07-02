import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.search import router as search_router
from src.database import db

app = FastAPI(
    title="Employee Search API",
    description="A RESTful API for searching employee records",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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