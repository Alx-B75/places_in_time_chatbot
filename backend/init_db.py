import os
import sys
import csv

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root_dir = os.path.dirname(current_dir)

if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

from backend.database import engine, engine_figure, SessionLocalFigure
from backend.models import Base, FigureBase, HistoricalFigure, User, Thread, FigureContext
from backend.vector.vector_ingest import ingest_all_context_chunks
from backend.tools.load_context_to_chroma import load_context_to_chroma



DATA_FILE = os.path.join(project_root_dir, "data", "figures_cleaned.csv")


def seed_figures():
    """
    Populates figures.db from figures_cleaned.csv if table is empty.
    """
    if not os.path.exists(DATA_FILE):
        print(f"⚠️ CSV file not found: {DATA_FILE}")
        return

    session = SessionLocalFigure()
    try:
        # removed for render deployment - if session.query(HistoricalFigure).first():
        #   print("ℹ️ historical_figures table already populated. Skipping seeding.")
        #  return

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

def init_db():
    """
    Creates all tables defined in the SQLAlchemy models for both databases,
    and seeds the figures.db with data from figures_cleaned.csv.
    """
    print("📂 Current working directory:", os.getcwd())
    print("📄 Target CHAT DB path:", os.path.abspath("./data/chat_history.db"))
    print("📄 Target FIGURE DB path:", os.path.abspath("./data/figures.db"))

    Base.metadata.create_all(bind=engine)
    print("✅ Initial chat history database tables created.")

    FigureBase.metadata.create_all(bind=engine_figure)
    print("✅ Initial historical figures database tables created.")

    seed_figures()
    load_context_to_chroma()

if __name__ == "__main__":
    init_db()
