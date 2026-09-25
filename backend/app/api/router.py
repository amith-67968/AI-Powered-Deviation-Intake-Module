from fastapi import APIRouter
from app.api.routes.deviations import router as deviations_router

api_router = APIRouter()
api_router.include_router(deviations_router)
