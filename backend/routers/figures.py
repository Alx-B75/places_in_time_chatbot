from fastapi import APIRouter, Depends, HTTPException, Request, Query
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

# We define the templates object here to make the router self-contained
templates = Jinja2Templates(directory="frontend/templates")


def get_figure_db():
    """Yields a session for the historical figures database."""
    db = FigureSessionLocal()
    try:
        yield db
    finally:
        db.close()


class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    figure_slug: str


# --- NEW ROUTE - Placed BEFORE the generic "/{slug}" route ---
@router.get("/ask", response_class=HTMLResponse)
def get_ask_figure_page(
    request: Request,
    figure_slug: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    thread_id: Optional[int] = None,
    db: Session = Depends(get_db_chat)
):
    """
    Handles the page for selecting or asking a historical figure.
    If no figure_slug is provided, it shows a selection page.
    Otherwise, it shows the chat interface for the selected figure.
    """
    # This logic shows the figure selection page
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

    # This logic handles displaying the chat page for a specific figure
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


@router.get("/", response_model=list[schemas.HistoricalFigureRead])
def read_all_figures(skip: int = 0, limit: int = 100, db: Session = Depends(get_figure_db)):
    """Retrieve a paginated list of all historical figures."""
    return crud.get_all_figures(db, skip=skip, limit=limit)


@router.get("/{slug}", response_model=schemas.HistoricalFigureDetail)
def read_figure_by_slug(slug: str, db: Session = Depends(get_figure_db)):
    """Retrieve a single historical figure and their context entries by slug."""
    figure = crud.get_figure_by_slug(db, slug=slug)
    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")
    return figure


@router.post("/search_context/")
def search_figure_context_route(query: SearchQuery):
    """Search the Chroma vector store for relevant historical figure context chunks."""
    results = search_figure_context(
        query=query.query,
        top_k=query.top_k,
        figure_slug=query.figure_slug
    )
    return results