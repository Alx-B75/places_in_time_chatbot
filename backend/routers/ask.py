from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db_chat, get_chroma_retriever
from backend.models import Chat
from backend.schemas import AskRequest, AskResponse
from openai import OpenAI
import os
from datetime import datetime
from backend.models_figure import HistoricalFigure
from backend.database import get_db_figure

router = APIRouter()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@router.post("/ask/", response_model=AskResponse)
def ask_question(
    request: AskRequest,
    db_chat: Session = Depends(get_db_chat),
    db_figure: Session = Depends(get_db_figure),
    retriever=Depends(get_chroma_retriever)
):
    """
    Handles a user question for a specific historical figure.
    Returns an AI-generated response using Chroma context filtered by figure.
    """

    figure = db_figure.query(HistoricalFigure).filter_by(slug=request.figure_slug).first()
    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")

    # System prompt based on figure
    persona_prompt = f"You are {figure.name}. Answer as this historical figure."  # Future: use figure.persona_prompt if defined

    # Search relevant figure context
    results = retriever.get_relevant_documents(
        request.question,
        filter={"figure_slug": request.figure_slug}
    )
    sources_used = []
    context_chunks = []
    for doc in results:
        context_chunks.append(doc.page_content)
        if doc.metadata.get("source"):
            sources_used.append(doc.metadata["source"])

    # Build GPT messages
    messages = [
        {"role": "system", "content": persona_prompt},
    ]
    for chunk in context_chunks:
        messages.append({"role": "system", "content": chunk})
    messages.append({"role": "user", "content": request.question})

    # Ask GPT
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    answer = completion.choices[0].message.content.strip()

    # Save to chat DB
    chat_entry = Chat(
        user_id=request.user_id,
        thread_id=request.thread_id,
        figure_slug=request.figure_slug,
        role="user",
        message=request.question,
        timestamp=datetime.utcnow()
    )
    db_chat.add(chat_entry)

    response_entry = Chat(
        user_id=request.user_id,
        thread_id=request.thread_id,
        figure_slug=request.figure_slug,
        role="assistant",
        message=answer,
        timestamp=datetime.utcnow()
    )
    db_chat.add(response_entry)
    db_chat.commit()

    return AskResponse(answer=answer, sources=sources_used)
