from typing import Optional

# login
class LoginRequestDTO:
    username: str
    password: str

# sign up
class RegisterRequestDTO:
    username: str
    email: str
    password: str
    display_name: Optional[str] = None

# create user
class CreateUserDTO:
    username: str
    email: str
    password: str
    display_name: Optional[str] = None
    role: Optional[str] = "public"

# update user
class UpdateUserDTO:
    email: Optional[str] = None
    password: Optional[str] = None
    display_name: Optional[str] = None
    role: Optional[str] = None

# all users
class UserResponseDTO:
    id: str
    username: str
    email: str
    display_name: Optional[str] = None
    role: str

