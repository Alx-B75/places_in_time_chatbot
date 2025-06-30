from sqlalchemy.orm import Session, selectinload
from backend import models, schemas
from backend.schemas import UserCreate
from backend.models import User


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

def get_user_by_username(db: Session, username: str):
    """
    Look up and return a user by username
    """

    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    """
    Look up and return a user by username
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user in the database.
    """
    db_user = User(
        username=user.username,
        hashed_password=user.hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_chat_message(db: Session, chat: schemas.ChatMessageCreate) -> models.Chat:
    """
    Create a new message entry for the role-based chat system.

    Args:
        db (Session): SQLAlchemy session.
        chat (ChatMessageCreate): A single chat message with role, content, and metadata.

    Returns:
        Chat: The stored message instance.
    """
    db_chat = models.Chat(
        user_id=chat.user_id,
        role=chat.role,
        message=chat.message,
        model_used=chat.model_used,
        source_page=chat.source_page,
        thread_id=chat.thread_id,
        summary_of=chat.summary_of
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_thread_by_id(db: Session, thread_id: int):
    """
    Get recent chat messages by thread id.
    """
    return db.query(models.Thread).filter(models.Thread.id == thread_id).first()


def get_messages_by_user(db: Session, user_id: int, limit: int = 50):
    """
    Get recent chat messages by user_id, ordered by timestamp.
    """
    return db.query(models.Chat)\
             .filter(models.Chat.user_id == user_id)\
             .order_by(models.Chat.timestamp.asc())\
             .limit(limit)\
             .all()


def get_messages_by_thread(db: Session, thread_id: int, limit: int = 50):
    return db.query(models.Chat)\
             .filter(models.Chat.thread_id == thread_id)\
             .order_by(models.Chat.timestamp.asc())\
             .limit(limit)\
             .all()


def get_messages_by_user(db: Session, user_id: int, limit: int = 50):
    """
    Retrieve chat messages for a specific user, ordered by timestamp ascending.

    Args:
        db (Session): SQLAlchemy DB session.
        user_id (int): The user whose messages to retrieve.
        limit (int): Max number of messages to return.

    Returns:
        List[Chat]: Messages ordered by timestamp ascending.
    """
    return (
        db.query(models.Chat)
        .filter(models.Chat.user_id == user_id)
        .order_by(models.Chat.timestamp.asc())
        .limit(limit)
        .all()
    )


def create_thread(db: Session, thread: schemas.ThreadCreate):
    """
    Create a new thread for a given user.
    """
    db_thread = models.Thread(
        user_id=thread.user_id,
        title=thread.title
    )
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)
    return db_thread


def get_threads_by_user(db: Session, user_id: int):
    """
    Retrieve all threads belonging to a user.
    """
    return (
        db.query(models.Thread)
        .filter(models.Thread.user_id == user_id)
        .order_by(models.Thread.created_at.desc())
        .all()
    )


def get_all_figures(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve all historical figures with optional pagination.
    """
    return (
        db.query(models.HistoricalFigure)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_figure_by_slug(db: Session, slug: str):
    """
    Retrieve a single historical figure by slug, including related context entries.
    """
    return (
        db.query(models.HistoricalFigure)
        .filter(models.HistoricalFigure.slug == slug)
        .options(selectinload(models.HistoricalFigure.contexts))
        .first()
    )
