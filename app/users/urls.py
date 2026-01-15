from fastapi import APIRouter, Depends
from .service import UsersService, get_users_service
from .models import User
from .schemas import UserCreate, UserRead
from ..auth.depends import get_oauth_admin, get_oauth_user
from typing import Annotated

router = APIRouter()

@router.get("/", response_model=list[UserRead])
async def get_users(_: Annotated[User, Depends(get_oauth_admin)],
                    service: UsersService = Depends(get_users_service)):
    return await service.get_users()

@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int,
                   current_user: User = Depends(get_oauth_user),
                   service: UsersService = Depends(get_users_service)):
    return await service.get_user(user_id, current_user)

@router.put("/{user_id}", response_model=UserRead)
async def edit_user(user_id: int,
                    user_data: UserCreate,
                    current_user: User = Depends(get_oauth_user),
                    service: UsersService = Depends(get_users_service)):
    return await service.edit_user(user_id, user_data, current_user)

@router.delete("/{user_id}")
async def delete_user(user_id: int,
                      current_user: User = Depends(get_oauth_user),
                      service: UsersService = Depends(get_users_service)):
    return await service.remove_user(user_id, current_user)