"""
generate_long_context_batch.py

Reads figures_cleaned.csv and generates long-form context entries using GPT.
Saves each entry to the FigureContext table in figures.db.
"""

import os
import csv
import time
import requests
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, FigureContext
from backend.tools.figure_enricher import FigureEnricher

load_dotenv()

# === Config ===
CSV_PATH = "data/figures_cleaned.csv"
DATABASE_PATH = "data/figures.db"
MODEL = "gpt-4o"

# === Init ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
engine = create_engine(f"sqlite:///{DATABASE_PATH}")
SessionLocal = sessionmaker(bind=engine)


def get_full_wikipedia_text(name: str) -> str:
    """
    Fetches the full Wikipedia text content for a given figure.
    """
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&format=json&titles={name}"
        response = requests.get(url)
        if response.status_code == 200:
            pages = response.json()["query"]["pages"]
            for page in pages.values():
                return page.get("extract", "")
    except Exception as e:
        print(f"[Wikipedia full text error for {name}] {e}")
    return ""


def get_dbpedia_abstract(dbpedia_url: str) -> str:
    """
    Fetches the DBpedia abstract (rdfs:comment) if available.
    """
    try:
        response = requests.get(dbpedia_url)
        if response.status_code != 200:
            return ""
        data = response.json()
        for entity in data.values():
            comments = entity.get("rdfs:comment") or entity.get("http://www.w3.org/2000/01/rdf-schema#comment")
            if comments:
                if isinstance(comments, dict):
                    comments = [comments]
                for comment in comments:
                    if comment.get("lang") == "en":
                        return comment.get("value", "")
    except Exception as e:
        print(f"[DBpedia error] {e}")
    return ""


def build_prompt(wiki_text: str, dbpedia_text: str, style: str) -> str:
    """
    Builds the prompt to instruct GPT to rewrite content in a chosen style.
    """
    styles = {
        "kids": "Use short, clear sentences and a fun tone for curious kids aged 10 and up. Make it vivid and easy to picture.",
        "teen": "Use straightforward but engaging language suitable for teenagers. Include key historical insights.",
        "gen": "Use an accessible and informative tone suitable for a wide audience.",
        "schol": "Write in an academic tone suitable for scholars and advanced students, with context and detail."
    }
    return (
        f"{styles.get(style, styles['gen'])}\n\n"
        "Below is content from two sources about a historical figure.\n"
        "Please write a new, well-structured long-form summary suitable for an educational website.\n\n"
        f"Wikipedia content:\n{wiki_text[:3000] or '[None]'}\n\n"
        f"DBpedia content:\n{dbpedia_text or '[None]'}"
    )


def process_figure(name: str, main_site: str, style: str, session):
    """
    Processes one historical figure: fetch, generate, and store.
    """
    print(f"\n🔄 Processing: {name}")
    enricher = FigureEnricher(name)
    data = enricher.enrich()

    wiki_text = get_full_wikipedia_text(name)
    dbpedia_url = data["sources"].get("dbpedia", "")
    dbpedia_text = get_dbpedia_abstract(dbpedia_url)

    if not wiki_text and not dbpedia_text:
        print(f"❌ No usable source text found for {name}")
        return

    prompt = build_prompt(wiki_text, dbpedia_text, style)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()

        context_entry = FigureContext(
            figure_slug=data["slug"],
            source_name="gpt-rewrite",
            source_url="",
            content_type="long_context",
            content=content,
            is_manual=0
        )
        session.add(context_entry)
        session.commit()
        print(f"✅ Saved long-form context for {name}")

    except Exception as e:
        print(f"❌ GPT error for {name}: {e}")
        return


def main():
    style = input("Select style for rewrite (kids / teen / gen / schol): ").strip().lower()
    if style not in ["kids", "teen", "gen", "schol"]:
        print("❌ Invalid style.")
        return

    if not os.path.exists(CSV_PATH):
        print(f"❌ Missing CSV file at {CSV_PATH}")
        return

    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        session = SessionLocal()
        for row in reader:
            name = row["name"].strip()
            main_site = row["main_site"].strip()
            try:
                process_figure(name, main_site, style, session)
                time.sleep(1.5)  # polite rate limit
            except Exception as e:
                print(f"❌ Error with {name}: {e}")
        session.close()
        print("\n🎉 Batch processing complete.")


if __name__ == "__main__":
    main()
