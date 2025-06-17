"""
compare_summaries.py

Fetch and compare summaries from Wikipedia, DBpedia, and a manual source.
Use GPT to rewrite a unified summary and save it to figures.db.
"""

import os
import json
import requests
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import FigureContext, Base
from backend.tools.figure_enricher import FigureEnricher
from dotenv import load_dotenv

load_dotenv()

# Setup OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database setup
DATABASE_PATH = "data/figures.db"
engine = create_engine(f"sqlite:///{DATABASE_PATH}")
SessionLocal = sessionmaker(bind=engine)


def get_style_prompt(style_code: str) -> str:
    styles = {
        "kids": "Use short sentences, friendly tone, and simple words. Make it exciting, fun and interesting for kids aged 10+.",
        "teen": "Use clear language suitable for teenagers and younger students. Be engaging but not childish. Provide some historical insight.",
        "gen": "Write in an accessible and informative tone suitable for all ages.",
        "schol": "Write in a formal, academic tone. Include important historical context and nuance."
    }
    return styles.get(style_code, styles["gen"])


def fetch_dbpedia_summary(dbpedia_url: str) -> str:
    try:
        response = requests.get(dbpedia_url)
        if response.status_code != 200:
            return ""
        data = response.json()
        for entity in data.values():
            comments = (
                entity.get("rdfs:comment") or
                entity.get("http://www.w3.org/2000/01/rdf-schema#comment")
            )
            if comments:
                if isinstance(comments, dict):
                    comments = [comments]
                for comment in comments:
                    if comment.get("lang") == "en":
                        return comment.get("value", "")
    except Exception as e:
        print(f"DBpedia fetch error: {e}")
    return ""


def fetch_wikipedia_summary(wiki_api_url: str) -> str:
    try:
        response = requests.get(wiki_api_url)
        if response.status_code == 200:
            return response.json().get("extract", "")
    except Exception as e:
        print(f"[Wikipedia error] {e}")
    return ""


def display_section(title: str, content: str, color: str = "⬜"):
    print(f"\n{color} {title}\n" + "-" * (len(title) + 2))
    print(content or "No content available.")


def rewrite_summary_with_gpt(wiki_summary: str, dbpedia_summary: str, manual_summary: str, style_prompt: str) -> str:
    prompt = (
        f"{style_prompt}\n\n"
        "Here are three summaries of a historical figure:\n\n"
        "📘 Wikipedia:\n"
        f"{wiki_summary or '[none]'}\n\n"
        "📙 DBpedia:\n"
        f"{dbpedia_summary or '[none]'}\n\n"
        "📗 Manual:\n"
        f"{manual_summary or '[none]'}\n\n"
        "Now write one clear, well-written summary in the chosen style."
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


def save_rewritten_summary(slug: str, content: str):
    session = SessionLocal()
    context_entry = FigureContext(
        figure_slug=slug,
        source_name="gpt-rewrite",
        source_url="",
        content_type="summary_rewrite",
        content=content,
        is_manual=0
    )
    session.add(context_entry)
    session.commit()
    session.close()
    print("✅ Rewritten summary saved to DB.")


def main():
    name = input("Enter the figure's name: ").strip()
    enricher = FigureEnricher(name)
    data = enricher.enrich()

    wiki_summary = fetch_wikipedia_summary(data["sources"].get("wikipedia", ""))
    dbpedia_summary = fetch_dbpedia_summary(data["sources"].get("dbpedia", ""))
    manual_summary = input("Paste a manual summary if you have one (or leave blank): ").strip()

    print("\n📚 SUMMARY COMPARISON")
    print("======================")
    display_section("Wikipedia", wiki_summary, "🟦")
    display_section("DBpedia", dbpedia_summary, "🟨")
    display_section("Manual", manual_summary, "🟩")

    choice = input("\nDo you want to generate and display a rewritten summary using GPT? (y/n): ").strip().lower()
    if choice != "y":
        return

    style = input("Choose style (kids / teen / gen / schol): ").strip().lower()
    style_prompt = get_style_prompt(style)

    new_summary = rewrite_summary_with_gpt(wiki_summary, dbpedia_summary, manual_summary, style_prompt)
    print("\n📝 GPT Rewritten Summary\n-------------------------")
    print(new_summary or "No rewritten summary generated.")

    save = input("\nSave this summary to the DB? (y/n): ").strip().lower()
    if save == "y" and new_summary:
        save_rewritten_summary(data["slug"], new_summary)


if __name__ == "__main__":
    main()
