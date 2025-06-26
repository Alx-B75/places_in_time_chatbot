"""
Exports all records from figures.db > historical_figures into figures_cleaned.csv
"""

import csv
from backend.database import SessionLocalFigure
from backend.models import HistoricalFigure

OUTPUT_CSV = "data/figures_cleaned.csv"

def export_figures():
    session = SessionLocalFigure()
    figures = session.query(HistoricalFigure).all()

    if not figures:
        print("⚠️ No figures found in the database.")
        return

    with open(OUTPUT_CSV, mode="w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            "name", "slug", "main_site", "related_sites", "era", "roles",
            "short_summary", "long_bio", "echo_story", "image_url", "sources",
            "wiki_links", "quote", "persona_prompt", "birth_year", "death_year", "verified"
        ])
        writer.writeheader()

        for fig in figures:
            writer.writerow({
                "name": fig.name,
                "slug": fig.slug,
                "main_site": fig.main_site,
                "related_sites": fig.related_sites,
                "era": fig.era,
                "roles": fig.roles,
                "short_summary": fig.short_summary,
                "long_bio": fig.long_bio,
                "echo_story": fig.echo_story,
                "image_url": fig.image_url,
                "sources": fig.sources,
                "wiki_links": fig.wiki_links,
                "quote": fig.quote,
                "persona_prompt": fig.persona_prompt,
                "birth_year": fig.birth_year,
                "death_year": fig.death_year,
                "verified": str(fig.verified)
            })

    session.close()
    print(f"✅ Exported {len(figures)} figures to {OUTPUT_CSV}")

if __name__ == "__main__":
    export_figures()
