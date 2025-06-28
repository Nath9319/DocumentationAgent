from fastapi import APIRouter
from .endpoints import statistics  # add others like basic_math if needed

api_router = APIRouter()
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
