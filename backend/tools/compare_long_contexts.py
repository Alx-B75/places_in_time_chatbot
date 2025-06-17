"""
compare_long_contexts.py

Fetch and compare long-form content from Wikipedia, DBpedia, and manual input.
Use GPT to rewrite a unified version in a given style and save to figures.db.
"""

import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import FigureContext
from backend.tools.figure_enricher import FigureEnricher

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATABASE_PATH = "data/figures.db"
engine = create_engine(f"sqlite:///{DATABASE_PATH}")
SessionLocal = sessionmaker(bind=engine)


def get_style_prompt(style_code: str) -> str:
    styles = {
        "kids": "Use short sentences, friendly tone, and simple words. Make it exciting and fun for kids aged 10+.",
        "teen": "Use clear language for teens. Be engaging, give context, but not too formal.",
        "gen": "Write in an accessible, informative tone suitable for general readers.",
        "schol": "Write in a formal academic tone, including historical nuance and depth."
    }
    return styles.get(style_code, styles["gen"])


def fetch_wikipedia_full(figure_name: str) -> str:
    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "titles": figure_name,
        "explaintext": 1,
        "format": "json",
        "redirects": 1
    }
    try:
        response = requests.get(url, params=params)
        pages = response.json().get("query", {}).get("pages", {})
        return next(iter(pages.values())).get("extract", "")
    except Exception as e:
        print(f"[Wikipedia full error] {e}")
        return ""


def fetch_dbpedia_abstract(dbpedia_url: str) -> str:
    try:
        response = requests.get(dbpedia_url)
        if response.status_code != 200:
            return ""
        data = response.json()
        for entity in data.values():
            abstract = entity.get("http://dbpedia.org/ontology/abstract")
            if abstract:
                for entry in abstract:
                    if entry.get("lang") == "en":
                        return entry.get("value", "")
    except Exception as e:
        print(f"[DBpedia abstract error] {e}")
    return ""


def rewrite_context_with_gpt(wiki: str, dbpedia: str, manual: str, style_prompt: str) -> str:
    prompt = (
        f"{style_prompt}\n\n"
        "Here are three long texts about a historical figure:\n\n"
        "📘 Wikipedia:\n"
        f"{wiki or '[none]'}\n\n"
        "📙 DBpedia:\n"
        f"{dbpedia or '[none]'}\n\n"
        "📗 Manual:\n"
        f"{manual or '[none]'}\n\n"
        "Now write a long, clear, engaging context text in the selected style."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[GPT error] {e}")
        return ""


def save_to_context(slug: str, content: str):
    session = SessionLocal()
    entry = FigureContext(
        figure_slug=slug,
        source_name="gpt-rewrite",
        source_url="",
        content_type="long_rewrite",
        content=content,
        is_manual=0
    )
    session.add(entry)
    session.commit()
    session.close()
    print("✅ Rewritten context saved to DB.")


def main():
    name = input("Enter the figure's name: ").strip()
    enricher = FigureEnricher(name)
    data = enricher.enrich()
    slug = data["slug"]
    print(f"\n🔎 Slug: {slug}")

    wiki_full = fetch_wikipedia_full(name)
    dbpedia_abstract = fetch_dbpedia_abstract(data["sources"].get("dbpedia", ""))
    manual_input = input("Paste long-form manual content (or leave blank):\n").strip()

    print("\n📚 CONTEXT PREVIEW\n====================")
    print("\n🟦 Wikipedia:\n", wiki_full[:500], "...\n")
    print("\n🟨 DBpedia:\n", dbpedia_abstract[:500], "...\n")
    print("\n🟩 Manual:\n", manual_input[:500], "...\n")

    if input("Continue to rewrite? (y/n): ").strip().lower() != "y":
        return

    style = input("Choose style (kids / teen / gen / schol): ").strip().lower()
    style_prompt = get_style_prompt(style)

    rewritten = rewrite_context_with_gpt(wiki_full, dbpedia_abstract, manual_input, style_prompt)

    print("\n📝 GPT Rewritten Context\n-------------------------\n")
    print(rewritten)

    if input("\nSave this to DB? (y/n): ").strip().lower() == "y":
        save_to_context(slug, rewritten)


if __name__ == "__main__":
    main()
