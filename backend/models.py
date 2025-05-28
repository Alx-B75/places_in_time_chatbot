from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Chat(Base):
    """
        Represents a single chat entry between a user and the chatbot.

        Fields:
            id (int): Primary key.
            user (str): Optional user identifier (e.g. username or session ID).
            question (str): The user's input question.
            answer (str): The chatbot's response.
            model_used (str): Identifier for the AI model used (e.g. 'gpt-4o-mini').
            source_page (str): Name or route of the page that triggered the chat.
            timestamp (datetime): Time the interaction was recorded (UTC).
        """
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    model_used = Column(String, nullable=True)
    source_page = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)