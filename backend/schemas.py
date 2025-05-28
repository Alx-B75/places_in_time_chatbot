from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatCreate(BaseModel):
    """
    This class is used when creating a new chat entry record.
    """
    user: Optional[str] = None
    question: str
    answer: str
    model_used: Optional[str] = None
    source_page: Optional[str] = None


class ChatRead(BaseModel):
    """
    This is used when returning a chat record entry from the database.
    """
    id: int
    user: Optional[str]
    question: str
    answer: str
    model_used: Optional[str]
    source_page: Optional[str]
    timestamp: datetime

    class Config:
        model_config = {
        "from_attributes": True
    }
