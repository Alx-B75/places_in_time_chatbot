from backend.database import SessionLocal
from backend import crud, schemas

def run_test():
    db = SessionLocal()

    print("✅ Creating user message...")
    user_msg = crud.create_chat_message(db, schemas.ChatMessageCreate(
        user_id=1,
        role="user",
        message="Was Alfred really that great?",
        model_used="gpt-4o-mini",
        source_page="test"
    ))
    print("User message stored:", user_msg.message)

    print("✅ Creating assistant message...")
    assistant_msg = crud.create_chat_message(db, schemas.ChatMessageCreate(
        user_id=1,
        role="assistant",
        message="Alfred the Great was notable for resisting Viking invasions...",
        model_used="gpt-4o-mini",
        source_page="test"
    ))
    print("Assistant message stored:", assistant_msg.message)

    print("✅ Retrieving message history...")
    messages = crud.get_messages_by_user(db, user_id=1)
    for m in messages:
        print(f"[{m.role}] {m.message}")

if __name__ == "__main__":
    run_test()
