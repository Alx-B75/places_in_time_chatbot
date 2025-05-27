from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from openai import OpenAI
import requests

load_dotenv()

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Query(BaseModel):
    """
        Simple model to take a question string from the user.
        """
    question: str


@app.post("/ask")
def ask_question(query: Query):
    """
        Takes a question and returns an answer from OpenAI GPT-4o-mini.

        Args:
            query: The user’s question.

        Returns:
            A dictionary with the answer or an error message.
        """
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
        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}

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

