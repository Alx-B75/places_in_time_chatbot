import json
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base
from .figures_database import FigureBase


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
        thread_id (int, optional): Foreign key to a thread grouping related messages.
        summary_of (int, optional): Foreign key referencing another Chat message that this message summarizes.
        timestamp (datetime): UTC time the message was stored.
        user (User): Relationship to the User who created the message.
        thread (Thread): Relationship to the Thread this message belongs to.
        summary_parent (Chat): Relationship to the parent Chat message being summarized, if applicable.
    """
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    role = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    model_used = Column(String, nullable=True)
    source_page = Column(String, nullable=True)
    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=True)
    summary_of = Column(Integer, ForeignKey("chats.id"), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")
    thread = relationship("Thread", back_populates="chats", lazy="joined")
    summary_parent = relationship("Chat", remote_side=[id], lazy="joined")




class User(Base):
    """
    Represents a user who can submit chats.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    chats = relationship("Chat", back_populates="user", cascade="all, delete")
    threads = relationship("Thread", back_populates="user", cascade="all, delete")


class Thread(Base):
    """
    Represents a conversation thread grouping related messages.
    """
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="threads")

    chats = relationship("Chat", back_populates="thread", cascade="all, delete-orphan")


class HistoricalFigure(FigureBase):
    """
    SQLAlchemy model representing a historical figure relevant to a site
    in the Places in Time project.

    JSON fields like roles, wiki_links, sources, and related_sites are stored as TEXT in SQLite
    and must be encoded/decoded manually.
    """
    __tablename__ = "historical_figures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    main_site = Column(String)
    related_sites = Column(Text)
    era = Column(String)
    roles = Column(Text)
    short_summary = Column(Text)
    long_bio = Column(Text)
    echo_story = Column(Text)
    image_url = Column(String)
    sources = Column(Text)
    wiki_links = Column(Text)
    quote = Column(Text)
    persona_prompt = Column(Text, nullable=True)
    birth_year = Column(Integer)
    death_year = Column(Integer)
    verified = Column(Integer, default=0)

    contexts = relationship(
        "FigureContext",
        backref="figure",
        primaryjoin="HistoricalFigure.slug == foreign(FigureContext.figure_slug)",
        lazy="selectin"
    )

    def to_dict(self):
        """
        Converts the figure instance to a Python dictionary with decoded JSON fields.
        """
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "main_site": self.main_site,
            "related_sites": json.loads(self.related_sites) if self.related_sites else [],
            "era": self.era,
            "roles": json.loads(self.roles) if self.roles else [],
            "short_summary": self.short_summary,
            "long_bio": self.long_bio,
            "echo_story": self.echo_story,
            "image_url": self.image_url,
            "sources": json.loads(self.sources) if self.sources else {},
            "wiki_links": json.loads(self.wiki_links) if self.wiki_links else {},
            "quote": self.quote,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
            "verified": bool(self.verified)
        }

    def from_dict(self, data: dict):
        """
        Populates fields from a Python dictionary, encodes JSON fields as strings.
        """
        self.name = data.get("name")
        self.slug = data.get("slug")
        self.main_site = data.get("main_site")
        self.related_sites = json.dumps(data.get("related_sites", []))
        self.era = data.get("era")
        self.roles = json.dumps(data.get("roles", []))
        self.short_summary = data.get("short_summary")
        self.long_bio = data.get("long_bio")
        self.echo_story = data.get("echo_story")
        self.image_url = data.get("image_url")
        self.sources = json.dumps(data.get("sources", {}))
        self.wiki_links = json.dumps(data.get("wiki_links", {}))
        self.quote = data.get("quote")
        self.birth_year = data.get("birth_year")
        self.death_year = data.get("death_year")
        self.verified = 1 if data.get("verified") else 0

class FigureContext(FigureBase):
    """
    SQLAlchemy model representing addtnl cntxt data for a historical figure.
    Stores orig source content for use in chatbot for grounding and detail.
    """
    __tablename__ = "figure_contexts"

    id = Column(Integer, primary_key=True)
    figure_slug = Column(String, index=True)
    source_name = Column(String)
    source_url = Column(String)
    content_type = Column(String)
    content = Column(Text)
    is_manual = Column(Integer, default=0)


