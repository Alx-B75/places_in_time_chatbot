import json
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class HistoricalFigure(Base):
    __tablename__ = "historical_figures"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    main_site = Column(String)
    related_sites = Column(Text)
    era = Column(String)
    roles = Column(Text)
    short_summary = Column(Text)
    long_bio = Column(Text)
    echo_story = Column(Text)
    image_url = Column(String)
    sources = Column(Text)
    wiki_links = Column(Text)
    quote = Column(Text)
    birth_year = Column(Integer)
    death_year = Column(Integer)
    verified = Column(Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "main_site": self.main_site,
            "related_sites": json.loads(self.related_sites) if self.related_sites else [],
            "era": self.era,
            "roles": json.loads(self.roles) if self.roles else [],
            "short_summary": self.short_summary,
            "long_bio": self.long_bio,
            "echo_story": self.echo_story,
            "image_url": self.image_url,
            "sources": json.loads(self.sources) if self.sources else {},
            "wiki_links": json.loads(self.wiki_links) if self.wiki_links else {},
            "quote": self.quote,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
            "verified": bool(self.verified)
        }

    def from_dict(self, data: dict):
        self.name = data.get("name")
        self.slug = data.get("slug")
        self.main_site = data.get("main_site")
        self.related_sites = json.dumps(data.get("related_sites", []))
        self.era = data.get("era")
        self.roles = json.dumps(data.get("roles", []))
        self.short_summary = data.get("short_summary")
        self.long_bio = data.get("long_bio")
        self.echo_story = data.get("echo_story")
        self.image_url = data.get("image_url")
        self.sources = json.dumps(data.get("sources", {}))
        self.wiki_links = json.dumps(data.get("wiki_links", {}))
        self.quote = data.get("quote")
        self.birth_year = data.get("birth_year")
        self.death_year = data.get("death_year")
        self.verified = 1 if data.get("verified") else 0

# Create engine and session
engine = create_engine("sqlite:///figures_test.db")
Base.metadata.create_all(bind=engine)

print("Table 'historical_figures' created successfully.")
