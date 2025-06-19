from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas, crud
from backend.figures_database import FigureSessionLocal
from backend.vector.context_retriever import search_figure_context
from pydantic import BaseModel

router = APIRouter(
    prefix="/figures",
    tags=["Figures"]
)

def get_figure_db():
    """
    Yields a session for the historical figures database.
    """
    db = FigureSessionLocal()
    try:
        yield db
    finally:
        db.close()


class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    figure_slug: str


@router.get("/", response_model=list[schemas.HistoricalFigureRead])
def read_all_figures(skip: int = 0, limit: int = 100, db: Session = Depends(get_figure_db)):
    """
    Retrieve a paginated list of all historical figures.
    """
    return crud.get_all_figures(db, skip=skip, limit=limit)


@router.get("/{slug}", response_model=schemas.HistoricalFigureDetail)
def read_figure_by_slug(slug: str, db: Session = Depends(get_figure_db)):
    """
    Retrieve a single historical figure and their context entries by slug.
    """
    figure = crud.get_figure_by_slug(db, slug=slug)
    if not figure:
        raise HTTPException(status_code=404, detail="Figure not found")
    return figure


@router.post("/search_context/")
def search_figure_context_route(query: SearchQuery):
    """
    Search the Chroma vector store for relevant historical figure context chunks.

    Args:
        query (SearchQuery): User's question and optional top_k limit.

    Returns:
        List of matching context documents with metadata.
    """
    results = search_figure_context(
        query=query.query,
        top_k=query.top_k,
        figure_slug=query.figure_slug
    )
    return results
