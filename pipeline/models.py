from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class PaperSummary:
    journal: str
    title: str
    title_en: str
    title_zh: str
    authors: List[str]
    affiliations: List[str]
    abstract: str
    link: str
    date: str

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PaperSummary":
        return PaperSummary(
            journal=data.get("journal", ""),
            title=data.get("title", ""),
            title_en=data.get("title_en", data.get("title", "")),
            title_zh=data.get("title_zh", ""),
            authors=list(data.get("authors", [])),
            affiliations=list(data.get("affiliations", [])),
            abstract=data.get("abstract", ""),
            link=data.get("link", ""),
            date=data.get("date", datetime.utcnow().date().isoformat()),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "journal": self.journal,
            "title": self.title,
            "title_en": self.title_en,
            "title_zh": self.title_zh,
            "authors": self.authors,
            "affiliations": self.affiliations,
            "abstract": self.abstract,
            "link": self.link,
            "date": self.date,
        }
