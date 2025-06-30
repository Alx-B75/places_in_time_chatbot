from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UserCreate(BaseModel):
    """
    Accepts user input for registration – expects a username and plain-text password.
    """
    username: str
    hashed_password: str


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
    message: str
    user_id: int
    model_used: Optional[str] = None
    source_page: Optional[str] = None
    figure_slug:Optional[str] = None


class ChatBase(BaseModel):
    """
    Shared base class for chat messages.
    """
    role: str
    message: str
    model_used: Optional[str] = None
    source_page: Optional[str] = None
    thread_id: Optional[int] = None
    summary_of: Optional[int] = None


class ChatMessageCreate(BaseModel):
    """
    Schema for creating a single chat message.
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
    Schema for reading a stored chat message with timestamp and ID.
    """
    id: int
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


class ThreadCreate(BaseModel):
    """
    Schema for creating a new conversation thread.
    """
    user_id: int
    title: Optional[str] = None


class ThreadRead(ThreadCreate):
    """
    Schema for reading an existing thread with metadata.
    """
    id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
        }


class FigureContextRead(BaseModel):
    """
    Schema to return context entries tied to a historical figure.
    """
    id: int
    figure_slug: str
    source_name: Optional[str]
    source_url: Optional[str]
    content_type: Optional[str]
    content: str
    is_manual: int

    class Config:
        from_attributes = True


class HistoricalFigureRead(BaseModel):
    """
    Summary schema for listing historical figures.
    """
    id: int
    name: str
    slug: str
    era: Optional[str]
    roles: Optional[str]
    image_url: Optional[str]
    short_summary: Optional[str]

    class Config:
        from_attributes = True


class HistoricalFigureDetail(HistoricalFigureRead):
    """
    Detailed schema for a single historical figure with full data and context entries.
    """
    long_bio: Optional[str]
    echo_story: Optional[str]
    quote: Optional[str]
    birth_year: Optional[int]
    death_year: Optional[int]
    main_site: Optional[str]
    related_sites: Optional[str]
    sources: Optional[str]
    wiki_links: Optional[str]
    verified: Optional[int]
    contexts: List[FigureContextRead] = []

class AskRequest(BaseModel):
    """
    Schema for incoming questions to the chatbot.
    Used by the /ask endpoint to structure the user's prompt.
    """
    user_id: int
    message: str
    figure_slug: Optional[str] = None
    source_page: Optional[str] = None
    model_used: Optional[str] = "gpt-4o-mini"
    thread_id: Optional[int] = None


class AskResponse(BaseModel):
    """
    Schema for chatbot responses returned by the /ask endpoint.
    Includes metadata and the assistant's message.
    """
    id: int
    user_id: int
    role: str
    message: str
    model_used: Optional[str] = None
    source_page: Optional[str] = None
    thread_id: Optional[int] = None
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }
