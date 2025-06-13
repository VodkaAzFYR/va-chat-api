from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    nickname: str = Field(..., min_length=1)
    is_admin: bool = False  


class UserCreate(UserBase):
    password: str = Field(..., min_length=1)


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str  


class TokenData(BaseModel):
    user_id: Optional[int] = None


class GroupBase(BaseModel):
    name: str = Field(..., min_length=1)


class GroupCreate(GroupBase):
    pass


class GroupRead(GroupBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class GroupReadWithMembers(GroupRead):
    members: List[UserRead] = []

    class Config:
        orm_mode = True


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)


class PrivateMessageCreate(MessageBase):
    pass


class GroupMessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int
    timestamp: datetime
    sender_id: Optional[int]
    receiver_id: Optional[int]
    group_id: Optional[int]
    user_id: Optional[int]

    class Config:
        orm_mode = True
