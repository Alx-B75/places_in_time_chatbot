"""
This script enriches a historical figure and inserts the result into the figures.db database.
Also adds full context and detail to separate table
"""

import sys
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.models import FigureContext, HistoricalFigure, Base
from backend.tools.figure_enricher import FigureEnricher

DATABASE_PATH = "data/figures.db"
engine = create_engine(f"sqlite:///{DATABASE_PATH}")
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

name = input("Enter the name of a historical figure to enrich and save: ")
extra_source = input("Paste any extra source URL (or leave blank): ").strip()

enricher = FigureEnricher(name)
enriched_data = enricher.enrich()

if extra_source:
    enriched_data.setdefault("sources", {})
    enriched_data["sources"]["manual"] = extra_source

enriched_data.update({
    "main_site": "Tower of London",
    "related_sites": ["Hever Castle"],
    "era": "Tudor",
    "roles": ["Queen", "Reformer"],
    "long_bio": enriched_data.get("short_summary", ""),
    "echo_story": "Some say Anne dropped her prayer book on purpose, to leave a final message.",
    "quote": "The executioner is, I believe, very expert...",
    "birth_year": 1501,
    "death_year": 1536,
    "verified": True
})

existing = session.query(HistoricalFigure).filter_by(slug=enriched_data["slug"]).first()

if existing:
    print(f"\nFigure '{name}' already exists in the database.")
    choice = input("Type 'u' to update, 's' to skip, or 'c' to continue and add only context: ").lower().strip()
    if choice == 's':
        print("Skipped.")
        session.close()
        sys.exit(0)
    elif choice == 'u':
        for key, value in enriched_data.items():
            if key in ["related_sites", "roles", "sources", "wiki_links"]:
                setattr(existing, key, json.dumps(value))
            else:
                setattr(existing, key, value)
        session.commit()
        print("Figure updated.")
    elif choice == 'c':
        context_entries = []

        if enriched_data.get("long_bio"):
            context_entries.append(FigureContext(
                figure_slug=enriched_data["slug"],
                source_name="Wikipedia",
                source_url=enriched_data["sources"].get("wikipedia", ""),
                content_type="long_bio",
                content=enriched_data["long_bio"],
                is_manual=0
            ))

        if enriched_data.get("echo_story"):
            context_entries.append(FigureContext(
                figure_slug=enriched_data["slug"],
                source_name="Generated",
                source_url="",
                content_type="echo_story",
                content=enriched_data["echo_story"],
                is_manual=0
            ))

        if extra_source:
            context_entries.append(FigureContext(
                figure_slug=enriched_data["slug"],
                source_name="Manual",
                source_url=extra_source,
                content_type="link",
                content="",
                is_manual=1
            ))

        if context_entries:
            session.add_all(context_entries)
            session.commit()
            print(f"Added {len(context_entries)} context entries for '{enriched_data['name']}'.")

        session.close()
        sys.exit(0)
    else:
        print("Invalid option. Aborting.")
        session.close()
        sys.exit(1)
else:
    figure = HistoricalFigure()
    figure.from_dict(enriched_data)
    session.add(figure)
    session.commit()
    print("Figure inserted.")

inserted = session.query(HistoricalFigure).filter_by(slug=enriched_data["slug"]).first()
print(json.dumps(inserted.to_dict(), indent=2))

for source_name, source_url in enriched_data.get("sources", {}).items():
    context_entry = FigureContext(
        figure_slug=enriched_data["slug"],
        source_name=source_name,
        source_url=source_url,
        content_type="json" if source_name in ["wikidata", "dbpedia"] else "html",
        content="",  # optional: fetch and insert raw content here later
        is_manual=1 if source_name == "manual" else 0
    )
    session.add(context_entry)

session.commit()

session.close()
