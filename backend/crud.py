from sqlalchemy.orm import Session
from backend import models, schemas


def create_chat(db: Session, chat: schemas.ChatCreate) -> models.Chat:
    """
    This creates a new chat entry in the chat database.

    Args:
        db: SQLAlchemy session.
        chat: Pydantic ChatCreate object.

    Returns:
        The created Chat model instance.
    """
    db_chat = models.Chat(
        user=chat.user,
        question=chat.question,
        answer=chat.answer,
        model_used=chat.model_used,
        source_page=chat.source_page
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


def get_all_chats(db: Session, limit: int = 100):
    """
    Returns the most recent chat entries.

    Args:
        db: SQLAlchemy session.
        limit: Maximum number of results to return.

    Returns:
        List of Chat records ordered by timestamp descending.
    """
    return db.query(models.Chat).order_by(models.Chat.timestamp.desc()).limit(limit).all()
