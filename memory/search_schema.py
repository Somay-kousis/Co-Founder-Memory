# memory/search_schema.py
from pydantic import BaseModel, Field
from typing import List

class SearchIntentProfile(BaseModel):
    web_queries: List[str] = Field(
        default=[], 
        description="A list of 2-3 precise search strings for DuckDuckGo to hunt down Hackathons, relevant open opportunities, tech articles, or missing packages based on active plans."
    )
    github_targets: List[str] = Field(
        default=[], 
        description="Explicit repo components, code frameworks, or internal tools from the user's focus list to parse or cross-examine."
    )