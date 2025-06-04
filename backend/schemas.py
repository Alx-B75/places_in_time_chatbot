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



class ChatMessageCreate(BaseModel):
    """
    Input schema for creating a single message in a conversation.
    Used internally or by /message endpoint.
    """
    user_id: Optional[int]
    role: str  # 'user', 'assistant', 'system', or 'summary'
    message: str
    model_used: Optional[str] = None
    source_page: Optional[str] = None
    thread_id: Optional[int] = None
    summary_of: Optional[str] = None

class ChatMessageRead(ChatMessageCreate):
    """
    Output schema for returning a stored chat message.
     """
    id: int
    timestamp: datetime

    model_config = {
        "from_attributes": True
        }


class ChatCompletionRequest(BaseModel):
    """
    Schema for submitting a new user message for LLM completion.
    """
    user_id: int
    message: str
    model_used: Optional[str] = "gpt-4o-mini"
    source_page: Optional[str] = None
    thread_id: Optional[int] = None
