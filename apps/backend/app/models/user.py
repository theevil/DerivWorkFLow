from datetime import datetime
from typing import Any, Optional

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    deriv_token: Optional[str] = None


class UserInDB(UserBase):
    id: Any = Field(alias="_id")
    hashed_password: str
    deriv_token: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class User(UserBase):
    id: str
    deriv_token: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_encoders": {ObjectId: str}
    }


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str
