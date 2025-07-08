import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta

# Local Imports
from backend import crud, schemas, models
from backend.figures_database import FigureSessionLocal
from backend.database import get_db_chat
from backend.templating import templates
from utils.security import (
    verify_password,
    hash_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
)
from backend.routers import figures, chat

# --- App Initialization ---
app = FastAPI()

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://places-in-time-chatbot.onrender.com",
        "http://localhost:8001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === AUTHENTICATION ROUTES ===

@app.post("/login")
async def login_for_access_token(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db_chat)):
    user = crud.get_user_by_username(db, username=username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id}

@app.post("/register")
async def register_user(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db_chat)):
    existing_user = crud.get_user_by_username(db, username=username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = hash_password(password)
    user_schema = schemas.UserCreate(username=username, hashed_password=hashed_pw)
    user = crud.create_user(db, user_schema)
    return {"message": f"User '{user.username}' created successfully"}


# === PROTECTED DATA ROUTE ===

@app.get("/threads/user/{user_id}", response_model=List[schemas.ThreadRead])
def list_user_threads(
    user_id: int,
    db: Session = Depends(get_db_chat),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access these threads")
    return crud.get_threads_by_user(db, user_id)


# === PAGE SERVING AND OTHER ROUTES ===

@app.get("/", response_class=FileResponse)
def index():
    return FileResponse(os.path.join("static_frontend", "index.html"))

@app.get("/user/{user_id}/threads", response_class=FileResponse)
def get_user_threads_page(user_id: int):
    path = os.path.join("static_frontend", "threads.html")
    return FileResponse(path, media_type="text/html")


# In backend/main.py

@app.get("/thread/{thread_id}", response_class=HTMLResponse)
def view_thread(thread_id: int, request: Request, db: Session = Depends(get_db_chat)):
    thread = crud.get_thread_by_id(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    figure = None
    if thread.figure_slug:
        # If the thread is linked to a figure, fetch the figure's details
        fig_db = FigureSessionLocal()
        try:
            figure = crud.get_figure_by_slug(fig_db, slug=thread.figure_slug)
        finally:
            fig_db.close()

    messages = crud.get_messages_by_thread(db, thread_id)

    return templates.TemplateResponse(
        "thread.html",
        {
            "request": request,
            "thread": thread,
            "messages": messages,
            "user_id": thread.user_id,
            "thread_id": thread.id,
            "figure": figure,  # Pass the figure object to the template
        },
    )

# --- API Routers & Static Files ---
app.include_router(figures.router)
app.include_router(chat.router)

app.mount("/", StaticFiles(directory="static_frontend"), name="static")

# --- Main Runner ---
if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)