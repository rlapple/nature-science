"""LLM prompt template for paper summarization."""

from __future__ import annotations

from dataclasses import dataclass

MAX_TITLE_LEN = 120
MAX_SUMMARY_LEN = 800
MAX_AFFILIATION_LEN = 200
MAX_COUNTRY_LEN = 100
MAX_KEYWORDS = 8
MAX_KEYWORD_LEN = 40


@dataclass(frozen=True)
class PaperMetadata:
    paper_id: str
    title: str
    abstract: str
    doi: str | None = None
    link: str | None = None


PROMPT_TEMPLATE = """You are a scientific summarizer.
Return ONLY valid JSON (no Markdown, no code fences, no commentary).
All strings must be plain text without Markdown formatting.

Required JSON fields:
- title_en
- title_zh
- summary_zh
- summary_en
- affiliation
- country
- keywords (array of strings)

Length limits:
- title_en/title_zh <= {max_title_len} characters
- summary_en/summary_zh <= {max_summary_len} characters
- affiliation <= {max_affiliation_len} characters
- country <= {max_country_len} characters
- keywords: 3-{max_keywords} items, each <= {max_keyword_len} characters

Paper input:
Title: {title}
Abstract: {abstract}
DOI: {doi}
Link: {link}
"""


def build_prompt(metadata: PaperMetadata) -> str:
    """Build the LLM prompt for a single paper."""
    return PROMPT_TEMPLATE.format(
        max_title_len=MAX_TITLE_LEN,
        max_summary_len=MAX_SUMMARY_LEN,
        max_affiliation_len=MAX_AFFILIATION_LEN,
        max_country_len=MAX_COUNTRY_LEN,
        max_keywords=MAX_KEYWORDS,
        max_keyword_len=MAX_KEYWORD_LEN,
        title=metadata.title.strip(),
        abstract=metadata.abstract.strip(),
        doi=metadata.doi or "",
        link=metadata.link or "",
    )
