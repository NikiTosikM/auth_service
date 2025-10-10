from fastapi import APIRouter

from auth.api.auth_router import router as auth_router
from auth.api.token_router import router as token_router



main_router = APIRouter()

main_router.include_router(auth_router)
main_router.include_router(token_router)