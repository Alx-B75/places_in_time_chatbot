"""
Simple script to display a historical figure and all associated context entries
from figures.db.
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Determine absolute path to the project root and the figures.db file
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATABASE_PATH = os.path.join(PROJECT_ROOT, "data", "figures.db")

print("Looking for DB at:", DATABASE_PATH)
print("Exists?", os.path.exists(DATABASE_PATH), "Is file?", os.path.isfile(DATABASE_PATH))

engine = create_engine(f"sqlite:///{DATABASE_PATH}")

from backend.models import HistoricalFigure, FigureContext

SessionLocal = sessionmaker(bind=engine)

def main():
    session = SessionLocal()
    slug = input("Enter the figure slug (e.g. 'richard-iii'): ").strip()
    fig = session.query(HistoricalFigure).filter_by(slug=slug).first()
    if not fig:
        print(f"No figure found with slug '{slug}'.")
        session.close()
        return

    print("\n=== Figure ===")
    print(fig.to_dict())

    contexts = session.query(FigureContext).filter_by(figure_slug=slug).all()
    if contexts:
        print("\n=== Context Entries ===")
        for c in contexts:
            print(f"- [{c.source_name} | {c.content_type} | manual={bool(c.is_manual)}]")
            print(f"  URL: {c.source_url}")
            if c.content:
                snippet = c.content[:200].replace("\n", " ")
                print(f"  Content snippet: {snippet}…")
    else:
        print("\nNo context entries found.")

    session.close()

if __name__ == "__main__":
    main()
