from sqlmodel import Session, select
from typing import Optional, List
import uuid

from backend.models import User, CreateUserDTO, UserLoginDTO, UserResponseDTO
from backend.utils import hash_password, verify_password, ConflictError, NotFoundError
from backend.services.permission_service import PermissionService


class UserService:
    """Service for user operations."""

    def __init__(self, session: Session):
        self.session = session

    def _populate_user_role_name(self, user: User) -> UserResponseDTO:
        """Convert User to UserResponseDTO and populate role_name."""
        user_response = UserResponseDTO.model_validate(user)
        if user.role_id:
            role = self.session.get(Role, user.role_id)
            if role:
                user_read.role_name = role.name
        return user_read

    def create_user(self, user_data: UserCreate) -> UserRead:
        """Create a new user."""
        # Check if username already exists
        statement = select(User).where(User.username == user_data.username)
        existing_user = self.session.exec(statement).first()
        if existing_user:
            raise ConflictError("Username already exists")

        # Check if email already exists
        statement = select(User).where(User.email == user_data.email)
        existing_user = self.session.exec(statement).first()
        if existing_user:
            raise ConflictError("Email already exists")

        # Get role_id from role_name - default to 'public' role if not specified
        role_id = None
        if user_data.role_name:
            # Use PermissionService to look up role by name
            permission_service = PermissionService(self.session)
            role = permission_service.get_role_by_name(user_data.role_name)
            if not role:
                raise NotFoundError(f"Role '{user_data.role_name}' not found")
            role_id = role.id
        else:
            # Find 'public' role ID as default
            public_role = self.session.exec(select(Role).where(Role.name == "public")).first()
            if public_role:
                role_id = public_role.id
            else:
                # Fallback to role ID 1 if 'public' role doesn't exist
                role_id = 1

        # Create user
        hashed_password = hash_password(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            display_name=user_data.display_name,
            bio=user_data.bio,
            role_id=role_id,
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        
        return self._populate_user_role_name(user)

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[UserRead]:
        """Get user by ID."""
        statement = select(User).where(User.id == user_id)
        user = self.session.exec(statement).first()
        if user:
            return self._populate_user_role_name(user)
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

    def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> UserRead:
        """Update user."""
        user = self.session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise NotFoundError("User not found")
        
        # Handle role_name to role_id conversion if role_name is provided
        role_id_to_set = None
        if user_data.role_name is not None:
            permission_service = PermissionService(self.session)
            role = permission_service.get_role_by_name(user_data.role_name)
            if not role:
                raise NotFoundError(f"Role '{user_data.role_name}' not found")
            role_id_to_set = role.id
        
        # Create a copy to avoid mutating the original object
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Remove role_name from update_data since it's not a field on the User model
        if 'role_name' in update_data:
            del update_data['role_name']
        
        # Add role_id if role_name was provided
        if role_id_to_set is not None:
            update_data['role_id'] = role_id_to_set
        
        # Prevent updating password_hash directly
        if 'password_hash' in update_data:
            del update_data['password_hash']

        # Handle password hashing if password is provided
        if 'password' in update_data and update_data['password']:
            update_data['password_hash'] = hash_password(update_data['password'])
            del update_data['password']

        # Apply updates to user
        for field, value in update_data.items():
            setattr(user, field, value)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        
        return self._populate_user_role_name(user)

    def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete user."""
        # Get the actual User object (not UserRead) for deletion
        user = self.session.exec(select(User).where(User.id == user_id)).first()
        if not user:
            raise NotFoundError("User not found")

        self.session.delete(user)
        self.session.commit()
        return True

    def list_users(self, skip: int = 0, limit: int = 100) -> List[UserRead]:
        """List users with pagination."""
        statement = select(User).offset(skip).limit(limit)
        users = list(self.session.exec(statement).all())
        return [self._populate_user_role_name(user) for user in users]
