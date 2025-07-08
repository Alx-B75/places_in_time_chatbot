
from dotenv import load_dotenv
load_dotenv()

import os
import sys
import csv

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.dirname(current_dir)

if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

# UPDATED: Imports are now separated to pull from the correct files
from backend.database import engine
from backend.figures_database import engine_figure, FigureSessionLocal
from backend.models import Base, FigureBase, HistoricalFigure, FigureContext
from tools.load_context_to_chroma import load_context_to_chroma

DATA_FILE = os.path.join(project_root_dir, "data", "figures_cleaned.csv")


def seed_figures():
    """
    Populates figures.db from figures_cleaned.csv if table is empty.
    """
    if not os.path.exists(DATA_FILE):
        print(f"⚠️ CSV file not found: {DATA_FILE}")
        return

    session = FigureSessionLocal()
    try:
        if session.query(HistoricalFigure).first():
            print("ℹ️ historical_figures table already populated. Skipping seeding.")
            return

        with open(DATA_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                figure = HistoricalFigure(
                    name=row['name'],
                    slug=row['slug'],
                    main_site=row.get('main_site'),
                    related_sites=row.get('related_sites'),
                    era=row.get('era'),
                    roles=row.get('roles'),
                    short_summary=row.get('short_summary'),
                    long_bio=row.get('long_bio'),
                    echo_story=row.get('echo_story'),
                    image_url=row.get('image_url'),
                    sources=row.get('sources'),
                    wiki_links=row.get('wiki_links'),
                    quote=row.get('quote'),
                    persona_prompt=row.get('persona_prompt'),
                    birth_year=row.get('birth_year'),
                    death_year=row.get('death_year'),
                    verified=row.get('verified', '').lower() == 'true'
                )
                session.add(figure)
                count += 1

            session.commit()
            print(f"✅ Seeded {count} historical figures.")
    finally:
        session.close()


def populate_figure_context_from_bio():
    """
    Create a default FigureContext entry for each HistoricalFigure
    using the long_bio as context.
    """
    session = FigureSessionLocal()
    try:
        figures = session.query(HistoricalFigure).all()
        count = 0
        for figure in figures:
            # Check if context for this bio already exists
            existing_context = session.query(FigureContext).filter_by(
                figure_slug=figure.slug,
                source_name="bio_csv"
            ).first()

            if not figure.long_bio or existing_context:
                continue

            context = FigureContext(
                figure_slug=figure.slug,
                source_name="bio_csv",
                source_url="",
                content_type="bio",
                content=figure.long_bio,
                is_manual=0
            )
            session.add(context)
            count += 1

        if count > 0:
            session.commit()
            print(f"✅ Populated {count} new figure contexts from long_bio.")
        else:
            print("ℹ️ No new contexts to populate from long_bio.")

    finally:
        session.close()


def init_db():
    """
    Creates all tables defined in the SQLAlchemy models for both databases,
    seeds figures from CSV, populates figure context, and loads vectors into Chroma.
    """
    print("--- Initializing Databases ---")

    # Create tables for the chat history database
    Base.metadata.create_all(bind=engine)
    print("✅ Chat history database tables created.")

    # Create tables for the figures database
    FigureBase.metadata.create_all(bind=engine_figure)
    print("✅ Historical figures database tables created.")

    # Seed data into the databases
    seed_figures()
    populate_figure_context_from_bio()

    # Load data into the vector store
    load_context_to_chroma()
    print("--- Database Initialization Complete ---")


if __name__ == "__main__":
    init_db()