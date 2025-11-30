"""Main FastAPI application."""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session
from .core.config import settings
from .core.database import get_db
from .api import workers, participants, payouts
from .services.prometheus_metrics import PrometheusExporter

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Monitoring and management system for Cocoon GPU Pool",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(workers.router, prefix=settings.API_V1_PREFIX)
app.include_router(participants.router, prefix=settings.API_V1_PREFIX)
app.include_router(payouts.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "metrics_url": "/metrics",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.PROJECT_NAME}


@app.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    """Prometheus metrics endpoint."""
    exporter = PrometheusExporter(db)
    metrics_data = exporter.get_metrics()
    return Response(content=metrics_data, media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
