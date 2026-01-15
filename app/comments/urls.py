from fastapi import APIRouter, Depends
from typing import Annotated
from ..users.models import User
from .schemas import CommentRead, CommentCreate, CommentBase
from .service import CommentService, get_comment_service
from ..auth.depends import get_oauth_user

router = APIRouter()

@router.post("/", response_model=CommentRead)
async def create_comment(
    comment: CommentCreate, 
    current_user: Annotated[User, Depends(get_oauth_user)],
    service: CommentService = Depends(get_comment_service)
):
    return await service.add_comment(comment, current_user.id) 

@router.get("/", response_model=list[CommentRead])
async def read_comments(
    _: Annotated[User, Depends(get_oauth_user)],
    service: CommentService = Depends(get_comment_service)
):
    return await service.get_comments() 

@router.put("/{comment_id}", response_model=CommentRead)
async def update_comment(
    comment_id: int, 
    comment_data: CommentBase, 
    current_user: Annotated[User, Depends(get_oauth_user)],
    service: CommentService = Depends(get_comment_service)
):
    return await service.edit_comment(comment_id, comment_data, current_user)

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int, 
    current_user: Annotated[User, Depends(get_oauth_user)],
    service: CommentService = Depends(get_comment_service)
):
    return await service.remove_comment(comment_id, current_user)