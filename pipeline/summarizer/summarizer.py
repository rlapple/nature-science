"""Summary pipeline utilities."""

from __future__ import annotations

from pathlib import Path

from .io import parse_llm_response, save_summary_json
from .template import PaperMetadata, build_prompt

SUMMARY_DIR = Path("data/summary")


def build_llm_request(metadata: PaperMetadata) -> str:
    """Return the prompt for the LLM request."""
    return build_prompt(metadata)


def write_summary_from_response(metadata: PaperMetadata, llm_response: str) -> Path:
    """Validate LLM output and write JSON to data/summary/<paper-id>.json."""
    payload = parse_llm_response(llm_response)
    output_path = SUMMARY_DIR / f"{_sanitize_paper_id(metadata.paper_id)}.json"
    save_summary_json(payload, output_path)
    return output_path


def _sanitize_paper_id(paper_id: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in paper_id)
