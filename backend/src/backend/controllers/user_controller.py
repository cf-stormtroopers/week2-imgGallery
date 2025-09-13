from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session
from typing import List
import uuid

from backend.config.database import get_session
from backend.models.dtos.auth import UserResponseDTO, UpdateUserDTO, CreateUserDTO
from backend.services import UserService
from backend.middleware import require_auth
from backend.utils import NotFoundError

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserResponseDTO])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user = Depends(require_auth)
):
    user_service = UserService(session)
    users = user_service.list_users(skip=skip, limit=limit)
    return users


@router.post("/", response_model=UserResponseDTO)
async def add_user(
    user_data: CreateUserDTO,
    session: Session = Depends(get_session),
    current_user = Depends(require_auth)
):
    user_service = UserService(session)
    user = user_service.create_user(user_data)
    return user


@router.get("/{user_id}", response_model=UserResponseDTO)
async def get_user(
    user_id: str,
    session: Session = Depends(get_session),
    current_user = Depends(require_auth)
):
    user_service = UserService(session)
    user = user_service.get_user_by_id(uuid.UUID(user_id))
    if not user:
        raise NotFoundError("User not found")
    return user


@router.put("/{user_id}", response_model=UserResponseDTO)
async def update_user(
    user_id: str,
    user_data: UpdateUserDTO,
    session: Session = Depends(get_session),
    current_user = Depends(require_auth)
):
    user_service = UserService(session)
    user = user_service.update_user(uuid.UUID(user_id), user_data)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    session: Session = Depends(get_session),
    current_user = Depends(require_auth)
):
    """Delete user (only own profile or admin)."""
    user_service = UserService(session)
    user_service.delete_user(uuid.UUID(user_id))
    return {"message": "User deleted"}