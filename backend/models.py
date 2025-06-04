from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Chat(Base):
    """
    Represents a single message in a chat conversation between a user and the chatbot.

    Fields:
        id (int): Primary key.
        user_id (int): Foreign key to the associated user.
        role (str): The role of the message sender ('user', 'assistant', 'system', 'summary').
        message (str): The content of the message.
        model_used (str, optional): Identifier for the AI model used (e.g. 'gpt-4o-mini').
        source_page (str, optional): Page or route that triggered the chat.
        thread_id (int, optional): Identifier for conversation threads.
        summary_of (str, optional): A reference for messages this is summarizing.
        timestamp (datetime): UTC time the message was stored.
    """
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    role = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    model_used = Column(String, nullable=True)
    source_page = Column(String, nullable=True)
    thread_id = Column(Integer, nullable=True)
    summary_of = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")



class User(Base):
    """
    Represents a user who can submit chats.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    chats = relationship("Chat", back_populates="user", cascade="all, delete")
