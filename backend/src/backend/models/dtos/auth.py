
from typing import Optional
from backend.models.base import BaseModel

class LoginRequestDTO(BaseModel):
    username: str
    password: str

class RegisterRequestDTO(BaseModel):
    username: str
    email: str
    password: str
    display_name: Optional[str] = None

class CreateUserDTO(BaseModel):
    username: str
    email: str
    password: str
    display_name: Optional[str] = None
    role: Optional[str] = "public"

class UpdateUserDTO(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    display_name: Optional[str] = None
    role: Optional[str] = None

class UserResponseDTO(BaseModel):
    id: str
    username: str
    email: str
    display_name: Optional[str] = None
    role: str

