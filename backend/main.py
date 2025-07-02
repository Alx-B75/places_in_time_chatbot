import os, sys
print("===== DEBUG: CWD =", os.getcwd())
print("===== DEBUG: DIR  =", os.listdir())
print("===== DEBUG: SYSP =", sys.path)

from fastapi import Depends, FastAPI, HTTPException, Form, Request, Query as FastQuery
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.orm import Session
from typing import Optional, List

# --- Local Imports ---
from backend import crud, schemas, models
from backend.database import get_db_chat, SessionLocalFigure
from backend.routers import figures
from backend.figures_database import FigureSessionLocal
from backend.vector.context_retriever import search_figure_context
from utils.security import hash_password, verify_password

import uvicorn

# --- App Initialization ---
app = FastAPI()
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
templates = Jinja2Templates(directory="frontend/templates")

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://places-in-time-chatbot.onrender.com"], # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Pydantic Models ---
class Query(BaseModel):
    question: str

#
# --- Authentication Endpoints ---
#
@app.post("/login")
async def login_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db_chat)):
    """
    Authenticates a user. On success, returns user data as JSON.
    """
    user = crud.get_user_by_username(db, username=username)

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    # On success, return user data instead of redirecting
    return JSONResponse(
        content={"user_id": user.id, "username": user.username}
    )


@app.post("/register")
async def register_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db_chat)):
    """
    Handles user registration. Checks if user exists, creates a new user,
    and returns user data as JSON.
    """
    existing_user = crud.get_user_by_username(db, username=username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")

    hashed_pw = hash_password(password)
    user_schema = schemas.UserCreate(username=username, hashed_password=hashed_pw)
    user = crud.create_user(db, user_schema)

    # On success, return user data instead of redirecting
    return JSONResponse(
        status_code=200,
        content={"user_id": user.id, "username": user.username}
    )

#
# --- Page Serving Endpoints ---
#
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    # This now just serves the main page. Login/Register are separate.
    return FileResponse(os.path.join("static_frontend", "index.html"))


@app.get("/user/{user_id}/threads", response_class=FileResponse)
def get_user_threads_page(user_id: int):
    """
    Serves the static threads.html page. The frontend JS will use the
    user_id to fetch the actual thread data from the API.
    """
    path = os.path.join("static_frontend", "threads.html")
    return FileResponse(path, media_type="text/html")


@app.get("/thread/{thread_id}", response_class=HTMLResponse)
def view_thread(thread_id: int, request: Request, db: Session = Depends(get_db_chat)):
    thread = db.query(models.Thread).filter(models.Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    messages = db.query(models.Chat).filter(models.Chat.thread_id == thread_id).order_by(models.Chat.timestamp.asc()).all()

    return templates.TemplateResponse("thread.html", {
        "request": request, "thread_id": thread_id, "thread": thread, "messages": messages, "user_id": thread.user_id,
    })

#
# --- API Endpoints for Data ---
#
@app.post("/ask", response_model=schemas.ChatMessageRead)
def ask_question(query: schemas.AskRequest, db: Session = Depends(get_db_chat)):
    # ... (omitted for brevity, your existing code is fine)
    pass # Your existing code for this function is fine

@app.get("/chats", response_model=List[schemas.ChatMessageRead])
def get_chats(limit: int = 100, db: Session = Depends(get_db_chat)):
    return crud.get_all_chats(db, limit=limit)

@app.post("/messages", response_model=schemas.ChatMessageRead)
def create_message(chat: schemas.ChatMessageCreate, db: Session = Depends(get_db_chat)):
    return crud.create_chat_message(db=db, chat=chat)

@app.get("/messages/user/{user_id}", response_model=List[schemas.ChatMessageRead])
def get_user_messages(user_id: int, limit: int = 50, db: Session = Depends(get_db_chat)):
    return crud.get_messages_by_user(db, user_id, limit)

@app.post("/threads", response_model=schemas.ThreadRead)
def create_thread(thread: schemas.ThreadCreate, db: Session = Depends(get_db_chat)):
    return crud.create_thread(db, thread)

@app.get("/threads/user/{user_id}", response_model=List[schemas.ThreadRead])
def list_user_threads(user_id: int, db: Session = Depends(get_db_chat)):
    return crud.get_threads_by_user(db, user_id)

@app.get("/messages/thread/{thread_id}", response_model=List[schemas.ChatMessageRead])
def get_messages_by_thread(thread_id: int, limit: int = 50, db: Session = Depends(get_db_chat)):
    return crud.get_messages_by_thread(db, thread_id, limit)

@app.post("/user/{user_id}/create_thread", response_class=RedirectResponse)
async def create_new_thread(user_id: int, request: Request, db: Session = Depends(get_db_chat)):
    """
    Handle submission of new thread form, save thread, then redirect.
    NOTE: This is a server-side form handler. The JS frontend will likely use POST /threads instead.
    """
    form_data = await request.form()
    title = form_data.get("title", "Untitled Thread")

    new_thread_schema = schemas.ThreadCreate(user_id=user_id, title=title)
    thread = crud.create_thread(db, new_thread_schema)

    # Redirects to the new thread's page
    return RedirectResponse(url=f"/thread/{thread.id}", status_code=303)

@app.post("/thread/{thread_id}/delete", response_class=RedirectResponse)
def delete_thread(thread_id: int, db: Session = Depends(get_db_chat)):
    thread = crud.get_thread_by_id(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    user_id = thread.user_id
    db.delete(thread)
    db.commit()
    return RedirectResponse(url=f"/user/{user_id}/threads", status_code=303)


# --- Other ---
@app.get("/download/chat_db", response_class=FileResponse)
def download_chat_db():
    return FileResponse(path="data/chat_history.db", filename="chat_history.db", media_type="application/octet-stream")


# --- Main Runner ---
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=10000, reload=True)