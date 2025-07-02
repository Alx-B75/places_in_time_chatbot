from fastapi import APIRouter, Depends, HTTPException, Request, Query, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from backend import models, schemas, crud
from backend.database import get_db_chat
from backend.figures_database import FigureSessionLocal
from backend.vector.context_retriever import search_figure_context
from pydantic import BaseModel

router = APIRouter(
    prefix="/figures",
    tags=["Figures"]
)

templates = Jinja2Templates(directory="frontend/templates")


def get_figure_db():
    db = FigureSessionLocal()
    try:
        yield db
    finally:
        db.close()


class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    figure_slug: str


@router.get("/ask", response_class=HTMLResponse)
def get_ask_figure_page(
        request: Request,
        figure_slug: Optional[str] = Query(None),
        user_id: Optional[str] = Query(None),
        thread_id: Optional[int] = None,
        db: Session = Depends(get_db_chat)
):
    if not figure_slug:
        figures = [
            {"slug": "emperor-hadrian", "name": "Emperor Hadrian"},
            {"slug": "flavius-cerialis", "name": "Flavius Cerialis"},
            {"slug": "guy-fawkes", "name": "Guy Fawkes"},
        ]
        return templates.TemplateResponse("figure_select.html", {
            "request": request,
            "figures": figures,
            "user_id_value": user_id
        })

    fig_db = FigureSessionLocal()
    figure = fig_db.query(models.HistoricalFigure).filter(models.HistoricalFigure.slug == figure_slug).first()
    fig_db.close()

    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")

    thread = crud.get_thread_by_id(db, thread_id) if thread_id else None
    messages = crud.get_messages_by_thread(db, thread_id) if thread else []

    user_id_value = user_id
    if messages and len(messages) > 0:
        user_id_value = messages[0].user_id

    return templates.TemplateResponse("ask_figure.html", {
        "request": request,
        "figure": figure,
        "thread": thread,
        "messages": messages,
        "user_id_value": user_id_value
    })


# --- NEWLY ADDED POST ROUTE ---
@router.post("/ask", response_class=HTMLResponse)
async def ask_figure_submit(
        request: Request,
        figure_slug: str = Form(...),
        user_id: int = Form(...),
        message: str = Form(...),
        thread_id: Optional[int] = Form(None),
        db: Session = Depends(get_db_chat)
):
    fig_db = FigureSessionLocal()
    figure = fig_db.query(models.HistoricalFigure).filter(models.HistoricalFigure.slug == figure_slug).first()
    fig_db.close()

    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")

    if thread_id:
        thread = crud.get_thread_by_id(db, thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
    else:
        thread_data = schemas.ThreadCreate(user_id=user_id, title=f"Chat with {figure.name}")
        thread = crud.create_thread(db, thread=thread_data)
        thread_id = thread.id

    crud.create_chat_message(db, schemas.ChatMessageCreate(
        user_id=user_id, role="user", message=message, thread_id=thread_id
    ))

    system_prompt = figure.persona_prompt or "You are a helpful historical guide."
    context_chunks = search_figure_context(query=message, figure_slug=figure_slug)
    context_text = "\n\n".join([chunk["content"] for chunk in context_chunks]) if context_chunks else ""

    all_messages = crud.get_messages_by_thread(db, thread_id)
    formatted_messages = [{"role": "system", "content": system_prompt}]
    if context_text:
        formatted_messages.append({"role": "system", "content": f"Relevant historical context:\n{context_text}"})

    formatted_messages.extend([{"role": m.role, "content": m.message} for m in all_messages])

    client = crud.get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o", messages=formatted_messages, temperature=0.7
    )
    reply = response.choices[0].message.content

    crud.create_chat_message(db, schemas.ChatMessageCreate(
        user_id=user_id, role="assistant", message=reply, thread_id=thread_id
    ))

    updated_messages = crud.get_messages_by_thread(db, thread_id)

    return templates.TemplateResponse("ask_figure.html", {
        "request": request,
        "figure": figure,
        "thread": thread,
        "messages": updated_messages,
        "user_id_value": user_id,
        "context_text": context_text
    })


@router.get("/", response_model=list[schemas.HistoricalFigureRead])
def read_all_figures(skip: int = 0, limit: int = 100, db: Session = Depends(get_figure_db)):
    return crud.get_all_figures(db, skip=skip, limit=limit)


@router.get("/{slug}", response_model=schemas.HistoricalFigureDetail)
def read_figure_by_slug(slug: str, db: Session = Depends(get_figure_db)):
    figure = crud.get_figure_by_slug(db, slug=slug)
    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")
    return figure


@router.post("/search_context/")
def search_figure_context_route(query: SearchQuery):
    results = search_figure_context(
        query=query.query,
        top_k=query.top_k,
        figure_slug=query.figure_slug
    )
    return results