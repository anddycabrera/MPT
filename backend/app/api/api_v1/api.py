from app.api.api_v1.routers import llm
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(llm.router)