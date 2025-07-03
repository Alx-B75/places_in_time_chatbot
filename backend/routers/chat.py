# backend/routers/chat.py

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from openai import OpenAI
import os

from backend import models, schemas, crud
from backend.database import get_db_chat

router = APIRouter(
    tags=["Chat"]
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/chat/complete", response_class=RedirectResponse)
def chat_complete(
    request: Request,
    db: Session = Depends(get_db_chat),
    user_id: int = Form(...),
    message: str = Form(...),
    thread_id: Optional[int] = Form(None),
):
    """
    Handles chat form submission from an existing thread page, saves the message,
    gets an AI response, and redirects back to the thread.
    """
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Save the user's message
    user_msg_schema = schemas.ChatMessageCreate(user_id=user_id, role="user", message=message, thread_id=thread_id)
    crud.create_chat_message(db, user_msg_schema)

    # Prepare message history for OpenAI
    messages = crud.get_messages_by_thread(db, thread_id)
    formatted_messages = [{"role": "system", "content": "You are a helpful and accurate historical guide."}]
    formatted_messages.extend([{"role": m.role, "content": m.message} for m in messages])

    # Get response from OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=formatted_messages,
        temperature=0.7
    )
    answer = response.choices[0].message.content

    # Save the assistant's message
    assistant_msg_schema = schemas.ChatMessageCreate(user_id=user_id, role="assistant", message=answer, thread_id=thread_id)
    crud.create_chat_message(db, assistant_msg_schema)

    return RedirectResponse(url=f"/thread/{thread_id}", status_code=303)