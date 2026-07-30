from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models import Role


# ---- Team ----

class TeamCreate(BaseModel):
    name: str


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


# ---- User ----

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: Role = Role.MEMBRO
    team_id: Optional[int] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: Role
    team_id: Optional[int] = None
    is_active: int


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[Role] = None
    team_id: Optional[int] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


# ---- Auth ----

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---- Report ----

class ReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    original_filename: str
    content_type: Optional[str] = None
    size_bytes: int
    owner_id: int
    team_id: int
    created_at: datetime
    owner_name: Optional[str] = None
    team_name: Optional[str] = None
