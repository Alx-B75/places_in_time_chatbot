import sys
import os
from datetime import datetime, UTC
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend import crud, models, schemas
from backend.database import Base, engine, SessionLocal


def test_create_and_read_chat():
    # Setup: Re-create the database for a clean test environment
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Open a session
    db: Session = SessionLocal()

    # Create a ChatCreate instance
    test_data = schemas.ChatCreate(
        user="test_user",
        question="Who built the Colosseum?",
        answer="The Romans built the Colosseum under Emperor Vespasian.",
        model_used="gpt-4o-mini",
        source_page="/colosseum"
    )

    # Create a chat record in the DB
    created = crud.create_chat(db, test_data)

    assert created.id is not None
    assert created.user == "test_user"
    assert created.model_used == "gpt-4o-mini"

    # Fetch it back
    all_chats = crud.get_all_chats(db)
    assert len(all_chats) == 1
    assert all_chats[0].question == "Who built the Colosseum?"

    # Cleanup
    db.close()
