from fastapi import Depends, FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.requests import Request
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
from sqlalchemy.orm import Session
from backend.database import get_db_chat, SessionLocal
from backend import crud, schemas, models
from backend.routers import figures
from typing import Optional
from backend.figures_database import FigureSessionLocal
from backend.models import HistoricalFigure
from backend.vector.context_retriever import search_figure_context

load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="frontend/templates")

origins = [
    "http://localhost:63342",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,   # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

class Query(BaseModel):
    """
    Simple model to take a question string from the user.
    """
    question: str


@app.post("/register_user", response_class=HTMLResponse)
async def register_user(request: Request, db: Session = Depends(get_db_chat)):
    """
    Register a new user from form data and redirect to their thread page.
    If the username already exists, show an error.
    """
    form_data = await request.form()
    username = form_data["username"]
    password = form_data["password"]

    existing_user = crud.get_user_by_username(db, username=username)
    if existing_user:
        return HTMLResponse(
            content=f"<h1>Error</h1><p>Username '{username}' already exists. Please go back and try a different name.</p>",
            status_code=400
        )

    user_data = schemas.UserCreate(username=username, password=password)
    user = crud.create_user(db, user_data)

    return RedirectResponse(url=f"/user/{user.id}/threads", status_code=303)


@app.post("/user/{user_id}/create_thread", response_class=HTMLResponse)
async def create_thread_for_user(user_id: int, request: Request, db: Session = Depends(get_db_chat)):
    """
    Handle creation of a new thread for a user and redirect to the thread view.
    """
    form_data = await request.form()
    title = form_data["title"]

    thread_data = schemas.ThreadCreate(user_id=user_id, title=title)
    thread = crud.create_thread(db, thread=thread_data)

    return RedirectResponse(url=f"/thread/{thread.id}", status_code=303)


@app.post("/thread/{thread_id}/delete", response_class=HTMLResponse)
def delete_thread(thread_id: int, db: Session = Depends(get_db_chat)):
    thread = crud.get_thread_by_id(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    db.delete(thread)
    db.commit()
    return RedirectResponse(url=f"/user/{thread.user_id}/threads", status_code=303)



@app.get("/user/{user_id}/threads", response_class=HTMLResponse)
def user_threads(request: Request, user_id: int, db: Session = Depends(get_db_chat)):
    """
    Display all chat threads associated with a given user ID.

    Args:
        request (Request): The incoming HTTP request object.
        user_id (int): The ID of the user whose threads are to be displayed.
        db (Session): The active SQLAlchemy database session.

    Returns:
        HTMLResponse: Rendered HTML page listing all chat threads for the user.

    Raises:
        HTTPException: If the user does not exist in the database (404 Not Found).
    """
    user = crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    threads = crud.get_threads_by_user(db, user_id=user_id)
    return templates.TemplateResponse("threads.html", {
        "request": request,
        "user": user,
        "threads": threads
    })


@app.post("/ask", response_model=schemas.ChatMessageRead)
def ask_question(query: schemas.AskRequest, db: Session = Depends(get_db_chat)):
    """
        Handle a user question by generating an AI response, storing both the question
        and answer as separate chat messages in the database, and returning the assistant's reply.

        Steps:
        - Validate that the user exists.
        - Optionally fetch a historical figure's persona prompt for impersonation.
        - Use OpenAI to generate a response based on the system prompt and user message.
        - Store two messages in the chat history: one for the user, one for the assistant.
        - Return the assistant's message as confirmation.

        Args:
            query (AskRequest): Incoming user message and metadata.
            db (Session): SQLAlchemy database session.

        Returns:
            ChatRead: The assistant's stored message.
        """
    user = crud.get_user_by_id(db, query.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    system_prompt = "You are a helpful and accurate historical guide."

    if query.figure_slug:
        from backend.figures_database import FigureSessionLocal
        from backend.models import HistoricalFigure

        fig_db = FigureSessionLocal()
        figure = fig_db.query(HistoricalFigure).filter(HistoricalFigure.slug == query.figure_slug).first()
        if figure and figure.persona_prompt:
            system_prompt = figure.persona_prompt
        fig_db.close()

    try:
        client = OpenAI()

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query.message}
            ],
            temperature=0.7
        )
        answer = response.choices[0].message.content

        user_msg = schemas.ChatMessageCreate(
            user_id=query.user_id,
            role="user",
            message=query.message,
            model_used=query.model_used,
            source_page=query.source_page,
            thread_id=query.thread_id
        )
        crud.create_chat_message(db, user_msg)

        assistant_msg = schemas.ChatMessageCreate(
            user_id=query.user_id,
            role="assistant",
            message=answer,
            model_used=query.model_used,
            source_page=query.source_page,
            thread_id=query.thread_id
        )
        db_chat = crud.create_chat_message(db, assistant_msg)
        return db_chat


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chats", response_model=list[schemas.ChatMessageRead])
def get_chats(limit: int = 100, db: Session = Depends(get_db_chat)):
    """
    Get the most recent chat entries from the database.
    """
    return crud.get_all_chats(db, limit=limit)

@app.post("/messages", response_model=schemas.ChatMessageRead)
def create_message(chat: schemas.ChatMessageCreate, db: Session = Depends(get_db_chat)):
    """
    Create a single role-based message (user, assistant, system, or summary).
    """
    return crud.create_chat_message(db=db, chat=chat)


@app.get("/messages/user/{user_id}", response_model=list[schemas.ChatMessageRead])
def get_user_messages(user_id: int, limit: int = 50, db: Session = Depends(get_db_chat)):
    """
    Retrieve up to 'limit' messages for a given user ID.
    """
    return crud.get_messages_by_user(db, user_id, limit)


@app.post("/chat/complete", response_class=HTMLResponse)
def chat_complete(
    request: Request,
    db: Session = Depends(get_db_chat),
    user_id: int = Form(...),
    message: str = Form(...),
    thread_id: Optional[int] = Form(None),
):
    """
    Handles chat form submission, saves the user's message, generates a response
    using the OpenAI API, saves the assistant's reply, and redirects to the thread page.
    """
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_msg = models.Chat(
        user_id=user_id,
        role="user",
        message=message,
        model_used="gpt-4o-mini",
        thread_id=thread_id,
        source_page="thread"
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    messages = db.query(models.Chat).filter(models.Chat.thread_id == thread_id).order_by(models.Chat.timestamp).all()
    formatted = [{"role": m.role, "content": m.message} for m in messages]
    formatted.insert(0, {"role": "system", "content": "You are a helpful and accurate historical guide."})

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=formatted,
        temperature=0.7
    )
    answer = response.choices[0].message.content

    assistant_msg = models.Chat(
        user_id=user_id,
        role="assistant",
        message=answer,
        model_used="gpt-4o-mini",
        thread_id=thread_id,
        source_page="thread"
    )
    db.add(assistant_msg)
    db.commit()

    return RedirectResponse(url=f"/thread/{thread_id}", status_code=303)



@app.post("/threads", response_model=schemas.ThreadRead)
def create_thread(thread: schemas.ThreadCreate, db: Session = Depends(get_db_chat)):
    """
    Create a new conversation thread for a user.
    """
    return crud.create_thread(db, thread)


@app.get("/threads/user/{user_id}", response_model=list[schemas.ThreadRead])
def list_user_threads(user_id: int, db: Session = Depends(get_db_chat)):
    """
    List all threads belonging to a specific user.
    """
    return crud.get_threads_by_user(db, user_id)


@app.get("/messages/thread/{thread_id}", response_model=list[schemas.ChatMessageRead])
def get_messages_by_thread(thread_id: int, limit: int = 50, db: Session = Depends(get_db_chat)):
    """
    Retrieve chat messages for a given thread.
    """
    return db.query(models.Chat)\
        .filter(models.Chat.thread_id == thread_id)\
        .order_by(models.Chat.timestamp.asc())\
        .limit(limit)\
        .all()


@app.post("/figures/ask", response_class=HTMLResponse)
async def ask_figure_submit(
    request: Request,
    figure_slug: str = Form(...),
    user_id: int = Form(...),
    message: str = Form(...),
    thread_id: Optional[int] = Form(None),
    db: Session = Depends(get_db_chat)
):
    fig_db = FigureSessionLocal()
    figure = fig_db.query(HistoricalFigure).filter(HistoricalFigure.slug == figure_slug).first()
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
        user_id=user_id,
        role="user",
        message=message,
        model_used="gpt-4o-mini",
        source_page="figures/ask",
        thread_id=thread_id
    ))

    system_prompt = figure.persona_prompt or "You are a helpful historical guide."

    context_chunks = search_figure_context(query=message, figure_slug=figure_slug)
    context_text = "\n\n".join([chunk["content"] for chunk in context_chunks]) if context_chunks else ""

    all_messages = crud.get_messages_by_thread(db, thread_id)
    formatted = [{"role": m.role, "content": m.message} for m in all_messages]
    formatted = [{"role": "system", "content": system_prompt}]

    if context_text:
        formatted.append({
            "role": "system",
            "content": f"Relevant historical context:\n{context_text}"
        })

    formatted.extend([{"role": m.role, "content": m.message} for m in all_messages])

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=formatted,
        temperature=0.7
    )
    reply = response.choices[0].message.content

    crud.create_chat_message(db, schemas.ChatMessageCreate(
        user_id=user_id,
        role="assistant",
        message=reply,
        model_used="gpt-4o-mini",
        source_page="figures/ask",
        thread_id=thread_id
    ))

    updated_messages = crud.get_messages_by_thread(db, thread_id)

    user_id_value = user_id

    return templates.TemplateResponse("ask_figure.html", {
        "request": request,
        "figure": figure,
        "thread": thread,
        "messages": updated_messages,
        "user_id_value": user_id_value,
        "context_text": context_text
    })



@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db_chat)):
    threads = crud.get_threads_by_user(db, user_id=1)  # Replace 1 with session later
    return templates.TemplateResponse("index.html", {
        "request": request,
        "threads": threads
    })


@app.get("/thread/{thread_id}", response_class=HTMLResponse)
def view_thread(thread_id: int, request: Request, db: Session = Depends(get_db_chat)):
    thread = db.query(models.Thread).filter(models.Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    messages = db.query(models.Chat) \
        .filter(models.Chat.thread_id == thread_id) \
        .order_by(models.Chat.timestamp.asc()) \
        .all()

    return templates.TemplateResponse("thread.html", {
        "request": request,
        "thread_id": thread_id,
        "thread": thread,
        "messages": messages,
        "user_id": thread.user_id,  # needed in next step
    })

from typing import Optional
from fastapi import Query

@app.get("/figures/ask", response_class=HTMLResponse)
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
            "figures": figures
        })

    fig_db = FigureSessionLocal()
    figure = fig_db.query(HistoricalFigure).filter(HistoricalFigure.slug == figure_slug).first()
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




@app.post("/select_user")
def select_user(user_id: int = Form(...)):
    """
    Redirect to a user's thread list.
    """
    return RedirectResponse(url=f"/user/{user_id}/threads", status_code=303)


@app.get("/figures/chat", response_class=HTMLResponse)
def show_figure_chat(request: Request):
    """
    Show form to chat with a historical figure.
    """
    return templates.TemplateResponse("figure_chat.html", {"request": request})


@app.post("/register")
async def register_api(request: Request, db: Session = Depends(get_db_chat)):
    """
    Handle user registration by extracting username and password from the HTML form
    and creating a new user in the database.
    """
    form_data = await request.form()
    username = form_data.get("username")
    password = form_data.get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")

    user = crud.create_user(db, schemas.UserCreate(username=username, password=password))
    return RedirectResponse(f"/user/{user.id}/threads", status_code=303)


@app.get("/user/{user_id}/create_thread", response_class=HTMLResponse)
def get_create_thread_page(user_id: int, request: Request):
    """
    Display form to create a new thread for a given user.
    """
    return templates.TemplateResponse("create_thread.html", {"request": request, "user_id": user_id})


@app.post("/user/{user_id}/create_thread", response_class=HTMLResponse)
async def create_new_thread(user_id: int, request: Request, db: Session = Depends(get_db_chat)):
    """
    Handle submission of new thread form, save thread, then redirect.
    """
    form_data = await request.form()
    title = form_data["title"]

    new_thread = schemas.ThreadCreate(user_id=user_id, title=title)
    crud.create_thread(db, new_thread)

    return RedirectResponse(url=f"/user/{user_id}/threads", status_code=303)


app.include_router(figures.router)

