from datetime import datetime

from pydantic import BaseModel
from typing import List, Optional


class MessageBase(BaseModel):
    content: str


class Message(MessageBase):
    id: int
    time_sent: datetime

    class Config:
        orm_mode = True


class ConversationBase(BaseModel):
    sender_id: int
    recipient_id: int
    message_id: int


class Conversation(ConversationBase):
    messages: List[Message] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str


class UserLookup(BaseModel):
    username: Optional[str]
    email: Optional[str]


class UserId(BaseModel):
    id: int


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    conversations: List[Conversation] = []
    friends: List[UserBase] = []

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str


class TokenData(BaseModel):
    username: Optional[str] = None


class ConversationMessage(BaseModel):
    sender: str
    recipient: str
    content: str
    time_sent: datetime
