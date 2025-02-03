"""Main FastAPI application module."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import articles

app = FastAPI(
    title="Greek News NLP API",
    description="API for analyzing bias in Greek sports journalism",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "Greek News NLP API",
        "version": "0.1.0",
        "status": "active"
    }

# Include routers
app.include_router(articles.router, prefix="/api/v1", tags=["articles"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 