"""
figure_enricher.py

Script to enrich historical figure data using Wikipedia, Wikidata, and DBpedia.
Designed for use in the Places in Time project backend ingestion pipeline.
"""

import requests
import json
from urllib.parse import quote


class FigureEnricher:
    """
    A class to enrich historical figure data from external sources:
    Wikipedia, Wikidata, and DBpedia.
    """

    def __init__(self, figure_name: str):
        """
        Initialize the enricher with a figure's name.

        Args:
            figure_name (str): The full name of the historical figure.
        """
        self.name = figure_name
        self.data = {
            "name": figure_name,
            "slug": FigureEnricher.slugify(figure_name),
            "sources": {},
            "wiki_links": {},
        }

    @staticmethod
    def slugify(text: str) -> str:
        """
        Convert a name to a URL-friendly slug.

        Args:
            text (str): The text to slugify.

        Returns:
            str: The slugified version of the input text.
        """
        return text.lower().replace(' ', '-')

    def fetch_wikipedia_summary(self):
        """
        Fetch a short summary and image from the Wikipedia REST API.
        Populates short_summary, image_url, and source links.
        """
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(self.name)}"
        response = requests.get(url)

        if response.status_code == 200:
            result = response.json()
            self.data["short_summary"] = result.get("extract", "")
            self.data["image_url"] = result.get("thumbnail", {}).get("source", "")
            self.data["wiki_links"]["wikipedia"] = result.get("content_urls", {}).get("desktop", {}).get("page", "")
            self.data["sources"]["wikipedia"] = url

    def fetch_wikidata_id(self) -> str | None:
        """
        Use the Wikipedia API to retrieve the Wikidata Q-ID.

        Returns:
            str | None: The Wikidata Q-ID or None if not found.
        """
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageprops&format=json&titles={quote(self.name)}"
        response = requests.get(url)

        if response.status_code == 200:
            pages = response.json().get("query", {}).get("pages", {})
            for page in pages.values():
                wikidata_id = page.get("pageprops", {}).get("wikibase_item")
                if wikidata_id:
                    self.data["wiki_links"]["wikidata"] = f"https://www.wikidata.org/wiki/{wikidata_id}"
                    self.data["sources"]["wikidata"] = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
                    return wikidata_id
        return None

    def fetch_dbpedia_resource(self):
        """
        Fetch the DBpedia resource link if available.
        Adds DBpedia page and source URL to the data.
        """
        dbpedia_url = f"http://dbpedia.org/data/{quote(self.name.replace(' ', '_'))}.json"
        response = requests.get(dbpedia_url)

        if response.status_code == 200:
            self.data["wiki_links"]["dbpedia"] = f"http://dbpedia.org/page/{quote(self.name.replace(' ', '_'))}"
            self.data["sources"]["dbpedia"] = dbpedia_url

    def enrich(self) -> dict:
        """
        Run all enrichment steps.

        Returns:
            dict: A dictionary containing the enriched data.
        """
        self.fetch_wikipedia_summary()
        self.fetch_wikidata_id()
        self.fetch_dbpedia_resource()
        return self.data


if __name__ == "__main__":
    name_input = input("Enter the name of a historical figure: ")
    enricher = FigureEnricher(name_input)
    enriched_result = enricher.enrich()
    print(json.dumps(enriched_result, indent=2))
