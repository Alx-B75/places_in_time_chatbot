from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
from sqlalchemy.orm import Session
from backend.database import get_db, SessionLocal
from backend import crud, schemas, models


load_dotenv()

app = FastAPI()

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


from fastapi import HTTPException

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
    Retrieve up to 'limit' chat messages for a given user_id.
    """
    return crud.get_messages_by_user(db, user_id, limit)


@app.get("/messages/user/{user_id}", response_model=list[schemas.ChatMessageRead])
def get_user_messages(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve up to 'limit' messages for a given user ID.
    """
    return crud.get_messages_by_user(db, user_id, limit)


@app.post("/chat/complete", response_model=schemas.ChatMessageRead)
def complete_chat(request: schemas.ChatCompletionRequest, db: Session = Depends(get_db)):
    """
    Accept a new user message, retrieve chat history, call OpenAI, return and store assistant response.
    """
    # Store the user message first
    user_message = crud.create_chat_message(db, schemas.ChatMessageCreate(
        user_id=request.user_id,
        role="user",
        message=request.message,
        model_used=request.model_used,
        source_page=request.source_page,
        thread_id=request.thread_id
    ))

    # Retrieve recent message history
    history = crud.get_messages_by_user(db, request.user_id, limit=10)

    # Build OpenAI messages
    messages = [{"role": "system", "content": "You are a helpful and accurate historical guide."}]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.message})

    # Add the new user message last
    messages.append({"role": "user", "content": request.message})

    # Send to OpenAI
    try:
        response = client.chat.completions.create(
            model=request.model_used,
            messages=messages,
            temperature=0.7
        )
        answer = response.choices[0].message.content

        # Store assistant reply
        assistant_message = crud.create_chat_message(db, schemas.ChatMessageCreate(
            user_id=request.user_id,
            role="assistant",
            message=answer,
            model_used=request.model_used,
            source_page=request.source_page,
            thread_id=request.thread_id
        ))

        return assistant_message

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI call failed: {str(e)}")


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

