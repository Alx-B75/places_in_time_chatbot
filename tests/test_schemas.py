import sys
import os

# Ensure we can import from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, UTC
import pytest
from backend.schemas import ChatCreate, ChatRead


def test_chat_create_valid():
    chat = ChatCreate(
        question="Who built Stonehenge?",
        answer="The builders of Stonehenge remain unknown.",
        user="alexanderbunting",
        model_used="gpt-4o-mini",
        source_page="/stonehenge"
    )
    assert chat.user == "alexanderbunting"
    assert chat.model_used == "gpt-4o-mini"


def test_chat_read_valid():
    chat_resp = ChatRead(
        id=42,
        user="alex",
        question="Who built Stonehenge?",
        answer="The builders of Stonehenge remain unknown.",
        model_used="gpt-4o-mini",
        source_page="/stonehenge",
        timestamp=datetime.now(UTC)
    )
    assert isinstance(chat_resp.timestamp, datetime)
    assert chat_resp.id == 42


def test_chat_create_invalid_field_type():
    with pytest.raises(ValueError):
        ChatCreate(
            question=12345,  # should be str
            answer="Valid answer",
            user="alex",
            model_used="gpt-4o-mini",
            source_page="/test"
        )
