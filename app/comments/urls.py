from fastapi import APIRouter, Depends, HTTPException
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
    new_comment =  await service.add_comment(comment, current_user.id) 
    if not new_comment:
        raise HTTPException(status_code=404, detail="News not found")
    return new_comment

@router.get("/", response_model=list[CommentRead])
async def read_comments(
    #_: Annotated[User, Depends(get_oauth_user)],
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
    new_comment =  await service.edit_comment(comment_id, comment_data, current_user)
    if not new_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return new_comment

@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int, 
    current_user: Annotated[User, Depends(get_oauth_user)],
    service: CommentService = Depends(get_comment_service)
):
    new_comment =  await service.remove_comment(comment_id, current_user)
    if not new_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return new_comment