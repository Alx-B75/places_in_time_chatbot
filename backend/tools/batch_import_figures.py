"""
batch_import_figures.py

Batch loads historical figures and GPT-rewritten summaries into the figures.db.
Expects a CSV with at least 'name' and 'main_site' columns.
"""

import os
import csv
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, HistoricalFigure, FigureContext
from backend.tools.figure_enricher import FigureEnricher
from backend.tools.compare_summaries import (
    fetch_wikipedia_summary,
    fetch_dbpedia_summary,
    get_style_prompt,
    rewrite_summary_with_gpt,
)
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = "data/figures.db"
CSV_FILE = "data/figures_cleaned.csv"
STYLE = "gen"  # change to 'kids', 'teen', 'schol' if needed

engine = create_engine(f"sqlite:///{DATABASE_PATH}")
SessionLocal = sessionmaker(bind=engine)
style_prompt = get_style_prompt(STYLE)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def process_row(row, session):
    name = row["name"].strip()
    site = row["main_site"].strip()

    enricher = FigureEnricher(name)
    data = enricher.enrich()

    wiki_summary = fetch_wikipedia_summary(data["sources"].get("wikipedia", ""))
    dbpedia_summary = fetch_dbpedia_summary(data["sources"].get("dbpedia", ""))
    manual_summary = ""  # Optional: add support later

    rewritten = rewrite_summary_with_gpt(wiki_summary, dbpedia_summary, manual_summary, style_prompt)

    # Insert or update historical figure
    existing = session.query(HistoricalFigure).filter_by(slug=data["slug"]).first()
    if existing:
        log(f"⚠️  Skipped (already exists): {name}")
        return

    figure = HistoricalFigure()
    figure.from_dict({
        **data,
        "main_site": site,
        "related_sites": [],
        "roles": [],
        "era": "",
        "long_bio": wiki_summary,
        "echo_story": "",
        "quote": "",
        "birth_year": None,
        "death_year": None,
        "verified": False,
    })
    session.add(figure)

    context_entries = []

    if wiki_summary:
        context_entries.append(FigureContext(
            figure_slug=data["slug"],
            source_name="wikipedia",
            source_url=data["sources"].get("wikipedia", ""),
            content_type="summary",
            content=wiki_summary,
            is_manual=0
        ))

    if dbpedia_summary:
        context_entries.append(FigureContext(
            figure_slug=data["slug"],
            source_name="dbpedia",
            source_url=data["sources"].get("dbpedia", ""),
            content_type="summary",
            content=dbpedia_summary,
            is_manual=0
        ))

    if rewritten:
        context_entries.append(FigureContext(
            figure_slug=data["slug"],
            source_name="gpt-rewrite",
            source_url="",
            content_type="summary_rewrite",
            content=rewritten,
            is_manual=0
        ))

    session.add_all(context_entries)
    session.commit()
    log(f"✅ Saved: {name}")


def main():
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV file not found at {CSV_FILE}")
        return

    session = SessionLocal()

    with open(CSV_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=1):
            name = row.get("name", "").strip()
            if not name:
                continue
            log(f"\n📘 [{i}] Processing: {name}")
            try:
                process_row(row, session)
            except Exception as e:
                log(f"❌ Error with {name}: {e}")
    session.close()
    log("🎉 Done.")


if __name__ == "__main__":
    main()
