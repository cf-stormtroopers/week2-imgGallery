from sqlmodel import Session, select
from typing import Optional, List
import uuid

from backend.models.models import User
from backend.models.dtos.auth import CreateUserDTO, UserResponseDTO, LoginRequestDTO, RegisterRequestDTO, UpdateUserDTO
from backend.utils import hash_password, verify_password, ConflictError, NotFoundError



class UserService:
    """Service for user operations."""

    def __init__(self, session: Session):
        self.session = session

    def _to_user_response(self, user: User) -> UserResponseDTO:
        return UserResponseDTO(
            id=str(user.id),
            username=user.username,
            email=user.email,
            display_name=user.display_name,
            role=user.role
        )

    def create_user(self, user_data: CreateUserDTO) -> UserResponseDTO:
        statement = select(User).where(User.username == user_data.username)
        existing_user = self.session.exec(statement).first()
        if existing_user:
            raise ConflictError("Username already exists")

        statement = select(User).where(User.email == user_data.email)
        existing_user = self.session.exec(statement).first()
        if existing_user:
            raise ConflictError("Email already exists")

        hashed_password = hash_password(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            display_name=user_data.display_name,
            role=user_data.role or "public"
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return self._to_user_response(user)


    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserResponseDTO]:
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()
        if user:
            return self._to_user_response(user)
        return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/password."""
        user = self.get_user_by_username(username)
        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        return user


    def update_user(self, user_id: uuid.UUID, user_data: UpdateUserDTO) -> UserResponseDTO:
        user = self.session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise NotFoundError("User not found")
        update_data = user_data.model_dump(exclude_unset=True)
        if 'password' in update_data and update_data['password']:
            update_data['password_hash'] = hash_password(update_data['password'])
            del update_data['password']
        for field, value in update_data.items():
            setattr(user, field, value)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return self._to_user_response(user)


    def delete_user(self, user_id: uuid.UUID) -> bool:
        user = self.session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise NotFoundError("User not found")
        self.session.delete(user)
        self.session.commit()
        return True

    def list_users(self, skip: int = 0, limit: int = 100) -> list[UserResponseDTO]:
        statement = select(User).offset(skip).limit(limit)
        users = list(self.session.exec(statement).all())
        return [self._to_user_response(user) for user in users]
