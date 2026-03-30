from fastapi import APIRouter

from app.api.endpoints import auth, county_configs, dashboard, ingestion, leads, letters, notifications, responses, tracking

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(county_configs.router, tags=["county-configs"])
api_router.include_router(leads.router, tags=["leads"])
api_router.include_router(letters.router, tags=["letters"])
api_router.include_router(tracking.router, tags=["tracking"])
api_router.include_router(notifications.router, tags=["notifications"])
api_router.include_router(responses.router, tags=["responses"])
api_router.include_router(ingestion.router, tags=["ingestion"])
