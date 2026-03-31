from typing import Optional

from pydantic import BaseModel


class UserCreateRequest(BaseModel):
    userId: Optional[str] = None
    name: str
    email: str


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
