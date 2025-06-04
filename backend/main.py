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
from backend.database import get_db, SessionLocal
from backend import crud, schemas, models
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

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Query(BaseModel):
    """
    Simple model to take a question string from the user.
    """
    question: str


@app.post("/register_user", response_class=HTMLResponse)
async def register_user(request: Request, db: Session = Depends(get_db)):
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
async def create_thread_for_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Handle creation of a new thread for a user and redirect to the thread view.
    """
    form_data = await request.form()
    title = form_data["title"]

    thread_data = schemas.ThreadCreate(user_id=user_id, title=title)
    thread = crud.create_thread(db, thread=thread_data)

    return RedirectResponse(url=f"/thread/{thread.id}", status_code=303)


@app.post("/register", response_model=schemas.UserRead)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with a username and password.
    Returns the user ID and username.
    """
    existing_user = crud.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    return crud.create_user(db, user)



@app.get("/user/{user_id}/threads", response_class=HTMLResponse)
def user_threads(request: Request, user_id: int, db: Session = Depends(get_db)):
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
def ask_question(query: schemas.ChatCreateRequest, db: Session = Depends(get_db)):
    """
    Receive a user question, generate an answer using GPT, save the chat linked to the user,
    and return the saved chat entry.
    """
    user = crud.get_user_by_id(db, query.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        response = client.chat.completions.create(
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
def get_chats(limit: int = 100, db: Session = Depends(get_db)):
    """
    Get the most recent chat entries from the database.
    """
    return crud.get_all_chats(db, limit=limit)

@app.post("/messages", response_model=schemas.ChatMessageRead)
def create_message(chat: schemas.ChatMessageCreate, db: Session = Depends(get_db)):
    """
    Create a single role-based message (user, assistant, system, or summary).
    """
    return crud.create_chat_message(db=db, chat=chat)


@app.get("/messages/user/{user_id}", response_model=list[schemas.ChatMessageRead])
def get_user_messages(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve up to 'limit' messages for a given user ID.
    """
    return crud.get_messages_by_user(db, user_id, limit)


@app.post("/chat/complete", response_class=HTMLResponse)
def chat_complete(
    request: Request,
    db: Session = Depends(get_db),
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
def create_thread(thread: schemas.ThreadCreate, db: Session = Depends(get_db)):
    """
    Create a new conversation thread for a user.
    """
    return crud.create_thread(db, thread)


@app.get("/threads/user/{user_id}", response_model=list[schemas.ThreadRead])
def list_user_threads(user_id: int, db: Session = Depends(get_db)):
    """
    List all threads belonging to a specific user.
    """
    return crud.get_threads_by_user(db, user_id)


@app.get("/messages/thread/{thread_id}", response_model=list[schemas.ChatMessageRead])
def get_messages_by_thread(thread_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve chat messages for a given thread.
    """
    return db.query(models.Chat)\
        .filter(models.Chat.thread_id == thread_id)\
        .order_by(models.Chat.timestamp.asc())\
        .limit(limit)\
        .all()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    threads = crud.get_threads_by_user(db, user_id=1)  # Replace 1 with session later
    return templates.TemplateResponse("index.html", {
        "request": request,
        "threads": threads
    })


@app.get("/thread/{thread_id}", response_class=HTMLResponse)
def view_thread(thread_id: int, request: Request, db: Session = Depends(get_db)):
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


@app.post("/register_user")
async def register_user(request: Request, db: Session = Depends(get_db)):
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
async def create_new_thread(user_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Handle submission of new thread form, save thread, then redirect.
    """
    form_data = await request.form()
    title = form_data["title"]

    new_thread = schemas.ThreadCreate(user_id=user_id, title=title)
    crud.create_thread(db, new_thread)

    return RedirectResponse(url=f"/user/{user_id}/threads", status_code=303)


# ---------------------------------------------------------------
# NOTE: Hugging Face endpoints (2 variants) currently commented out
# Reason:
#   - Model call to `flan-t5-large` and others returned 401 or 404
#   - Token was removed and public models tested without success
#   - Curl tests confirm issue is not on our side
#
# Next steps:
#   - Try a completely different approach or...
#   - Test again with `sshleifer/tiny-gpt2` or another known-safe model
#   - Confirm headers and token use are clean
#   - Optional: switch to LM Studio or run models locally
#
# TODO: Fix Hugging Face call and re-enable `/ask_hf`
# ---------------------------------------------------------------


"""@app.post("/ask_hf")
def ask_question_huggingface(query: Query):
    try:
        headers = {
            "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"
        }

        payload = {
            "inputs": f"{query.question}",
            "parameters": {"temperature": 0.7, "max_new_tokens": 256}
        }

        response = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-large",
            headers=headers,
            json=payload,
            timeout=60
        )

        # Handle non-JSON or failed responses
        if response.status_code != 200:
            return {
                "error": f"Hugging Face returned status code {response.status_code}",
                "detail": response.text
            }

        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            return {"answer": result[0]["generated_text"]}
        else:
            return {"error": "Unexpected response format", "raw": result}

    except Exception as e:
        return {"error": str(e)}"""


"""@app.post("/ask_hf")
def ask_question_huggingface(query: Query):
    try:
        headers = {"Content-Type": "application/json"}

        payload = {
            "inputs": f"{query.question}",
            "parameters": {"temperature": 0.7, "max_new_tokens": 50}
        }

        response = requests.post(
            "https://api-inference.huggingface.co/models/sshleifer/tiny-gpt2",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            return {
                "error": f"Hugging Face returned status code {response.status_code}",
                "detail": response.text
            }

        result = response.json()

        return {"answer": result[0]["generated_text"]}

    except Exception as e:
        return {"error": str(e)}"""

