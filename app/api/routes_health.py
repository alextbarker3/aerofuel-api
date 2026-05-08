from fastapi import APIRouter, Depends

from app.config import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Settings = Depends(get_settings)):
    return {
        "status": "ok",
        "service": "aerofuel-api",
        "version": settings.version,
        "environment": settings.environment,
    }


@router.get("/metadata", tags=["metadata"])
def metadata(settings: Settings = Depends(get_settings)):
    return {
        "name": settings.app_name,
        "version": settings.version,
        "description": "Lightweight aviation fuel intelligence API using synthetic data.",
        "safety_note": "Not valid for operational flight planning. Synthetic data only.",
    }
