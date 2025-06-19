from fastapi import Depends, FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.requests import Request
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import openai
from sqlalchemy.orm import Session
from backend.database import get_db_chat, SessionLocal
from backend import crud, schemas, models
from backend.routers import figures
from typing import Optional

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

openai.api_key = os.getenv("OPENAI_API_KEY")

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


@app.post("/ask", response_model=schemas.ChatRead)
def ask_question(query: schemas.ChatCreateRequest, db: Session = Depends(get_db_chat)):
    """
    Receive a user question, generate an answer using GPT, save the chat linked to the user,
    and return the saved chat entry.
    """
    user = crud.get_user_by_id(db, query.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful and accurate historical guide."},
                {"role": "user", "content": query.question}
            ],
            temperature=0.7
        )
        answer = response.choices[0].message.content

        chat = schemas.ChatCreate(
            question=query.question,
            answer=answer,
            user_id=query.user_id,
            model_used=query.model_used,
            source_page=query.source_page,
        )
        db_chat = crud.create_chat(db, chat)
        return db_chat

    except Exception as e:
        return {"error": str(e)}



@app.get("/chats", response_model=list[schemas.ChatRead])
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

    response = openai.chat.completions.create(
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



@app.post("/select_user")
def select_user(user_id: int = Form(...)):
    """
    Redirect to a user's thread list.
    """
    return RedirectResponse(url=f"/user/{user_id}/threads", status_code=303)


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

