"""
Prompt Testing Script for Places-in-Time Project
Supports OpenAI and OpenRouter (Claude, Gemini, Mistral, etc.)
"""

import os
import pandas as pd
from datetime import datetime, UTC
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# Define prompts
prompt_matrix = [
    {
        "technique": "Zero-shot",
        "prompt": "Explain what made Æthelflæd important in English history.",
    },
    {
        "technique": "Chain-of-thought",
        "prompt": "Let's think step by step. Why is Æthelflæd considered a key figure in early English history?",
    },
    {
        "technique": "Role prompting",
        "prompt": "You are a historian. Tell me why Æthelflæd is significant in medieval English history.",
    },
    {
        "technique": "Simple language",
        "prompt": "Explain who Æthelflæd was and why she matters, in a way a 10-year-old can understand.",
    },
    {
        "technique": "Impersonation",
        "prompt": "You are Æthelflæd, please stay in character. Explain who you are and your place in history as though you are speaking to an intelligent young child around 10-year-old.",
    }
]

# Define models — OpenAI and OpenRouter
models = [
    "gpt-4o",                                   # OpenAI
    "gpt-3.5-turbo",                            # OpenAI
    "anthropic/claude-3-opus",                  # OpenRouter
    "google/gemini-2.5-pro-exp-03-25",          # OpenRouter
    "mistralai/mistral-small-3.1-24b-instruct"  # OpenRouter
]

# Approximate cost per 1K tokens (USD)
cost_per_token = {
    "gpt-4o": 0.005,
    "gpt-3.5-turbo": 0.001,
    "anthropic/claude-3-opus": 0.010,
    "google/gemini-2.5-pro-exp-03-25": 0.0020,
    "mistralai/mistral-small-3.1-24b-instruct": 0.0008
}

results = []

for model in models:
    client = openrouter_client if "/" in model else openai_client
    for test in prompt_matrix:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": test["prompt"]}
                ],
                temperature=0.7
            )

            choice = response.choices[0].message
            usage = response.usage

            results.append({
                "timestamp": datetime.now(UTC).isoformat(),
                "technique": test["technique"],
                "model": model,
                "prompt": test["prompt"],
                "response": choice.content,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "cost_usd": round((usage.total_tokens / 1000) * cost_per_token.get(model, 0.001), 5),
            })

        except Exception as e:
            results.append({
                "timestamp": datetime.now(UTC).isoformat(),
                "technique": test["technique"],
                "model": model,
                "prompt": test["prompt"],
                "response": f"Error: {str(e)}",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "cost_usd": 0,
            })

df = pd.DataFrame(results)
output_path = os.path.join(os.path.dirname(__file__), "prompt_test_results.csv")
df.to_csv(output_path, index=False)

print(f"✅ Results saved to: {output_path}")
