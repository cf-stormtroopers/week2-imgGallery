from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session
from typing import List
import uuid

from backend.config.database import get_session
from backend.models import UserRead, UserUpdate, UserCreate
from backend.services import UserService
from backend.services.permission_service import PermissionService
from backend.middleware import require_auth
from backend.utils import NotFoundError


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserRead])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    session: Session = Depends(get_session),
    current_user = Depends(require_auth)
):
    """List users with pagination (admin only)."""
    # Check if user has admin permissions
    permission_service = PermissionService(session)
    permissions = permission_service.get_user_permissions(current_user)
    
    if "update_site_settings" not in permissions:
        raise HTTPException(status_code=403, detail="Admin permissions required to list users")
    
    user_service = UserService(session)
    users = user_service.list_users(skip=skip, limit=limit)
    return users


@router.post("/", response_model=UserRead)
async def add_user(
    user_data: UserCreate,
    session: Session = Depends(get_session),
    current_user = Depends(require_auth)
):
    """Create a new user (admin only)."""
    # Check if user has admin permissions
    permission_service = PermissionService(session)
    permissions = permission_service.get_user_permissions(current_user)
    
    if "update_site_settings" not in permissions:
        raise HTTPException(status_code=403, detail="Admin permissions required to create users")
    
    user_service = UserService(session)
    user = user_service.create_user(user_data)
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user = Depends(require_auth)
):
    """Get user by ID (own profile or admin)."""
    # Check if user has admin permissions or is viewing their own profile
    permission_service = PermissionService(session)
    permissions = permission_service.get_user_permissions(current_user)
    
    if current_user.id != user_id and "update_site_settings" not in permissions:
        raise HTTPException(status_code=403, detail="Admin permissions required to view other users")
    
    user_service = UserService(session)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise NotFoundError("User not found")
    
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
    current_user = Depends(require_auth)
):
    """Update user (only own profile or admin)."""
    # Check if user has admin permissions or is updating their own profile
    permission_service = PermissionService(session)
    permissions = permission_service.get_user_permissions(current_user)
    
    if current_user.id != user_id and "update_site_settings" not in permissions:
        raise HTTPException(status_code=403, detail="Admin permissions required to update other users")
    
    user_service = UserService(session)
    user = user_service.update_user(user_id, user_data)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    session: Session = Depends(get_session),
    current_user = Depends(require_auth)
):
    """Delete user (only own profile or admin)."""
    # Check if user has admin permissions or is deleting their own profile
    permission_service = PermissionService(session)
    permissions = permission_service.get_user_permissions(current_user)
    
    if current_user.id != user_id and "update_site_settings" not in permissions:
        raise HTTPException(status_code=403, detail="Admin permissions required to delete other users")
    
    user_service = UserService(session)
    user_service.delete_user(user_id)
    return {"message": "User deleted successfully"}
