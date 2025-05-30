from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    """
    Accepts user input for registration – expects a username and plain-text password.
    """
    username: str
    # will be hashed in another development
    password: str


class UserRead(BaseModel):
    """
    Returns user data after registration – excludes password.
    """
    id: int
    username: str

    model_config = {"from_attributes": True}


class ChatCreateRequest(BaseModel):
    """
    Input schema for /ask endpoint - client sends only these fields.
    """
    question: str
    user_id: int
    model_used: Optional[str] = None
    source_page: Optional[str] = None


class ChatCreate(BaseModel):
    """
    Internal schema used for DB creation.
    """
    question: str
    answer: str
    user_id: int
    model_used: Optional[str] = None
    source_page: Optional[str] = None


class ChatRead(BaseModel):
    """
    Output schema - data returned after creation or reading.
    """
    id: int
    question: str
    answer: str
    user_id: int
    model_used: Optional[str] = None
    source_page: Optional[str] = None
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }