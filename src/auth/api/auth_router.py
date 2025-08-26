from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schemas import UserSchema, UserResponce
from auth.api.dependencies import get_session_depen
from auth.service import UserAuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
async def register_user(
    user: Annotated[UserSchema, Body()],
    session: AsyncSession = Depends(get_session_depen)
) -> UserResponce :
    user_service = UserAuthService(session=session)
    
    created_user: UserResponce = await user_service.create_user(user_data=user)
    
    return created_user