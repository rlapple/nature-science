"""Utilities for validating and saving LLM summaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .template import (
    MAX_AFFILIATION_LEN,
    MAX_COUNTRY_LEN,
    MAX_KEYWORDS,
    MAX_KEYWORD_LEN,
    MAX_SUMMARY_LEN,
    MAX_TITLE_LEN,
)

REQUIRED_FIELDS = {
    "title_en",
    "title_zh",
    "summary_zh",
    "summary_en",
    "affiliation",
    "country",
    "keywords",
}


class SummaryValidationError(ValueError):
    """Raised when summary JSON fails validation."""


def parse_llm_response(raw_response: str) -> dict[str, Any]:
    """Parse and validate LLM JSON output.

    The LLM must return only a JSON object without Markdown or extra text.
    """
    stripped = raw_response.strip()
    if "```" in stripped:
        raise SummaryValidationError("Markdown code fences are not allowed.")
    if not stripped.startswith("{") or not stripped.endswith("}"):
        raise SummaryValidationError("Response must be a single JSON object.")

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise SummaryValidationError("Invalid JSON in response.") from exc

    validate_summary_payload(payload)
    return payload


def validate_summary_payload(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise SummaryValidationError("Summary payload must be a JSON object.")

    missing = REQUIRED_FIELDS - payload.keys()
    if missing:
        raise SummaryValidationError(f"Missing required fields: {sorted(missing)}")

    _validate_text_field(payload, "title_en", MAX_TITLE_LEN)
    _validate_text_field(payload, "title_zh", MAX_TITLE_LEN)
    _validate_text_field(payload, "summary_en", MAX_SUMMARY_LEN)
    _validate_text_field(payload, "summary_zh", MAX_SUMMARY_LEN)
    _validate_text_field(payload, "affiliation", MAX_AFFILIATION_LEN)
    _validate_text_field(payload, "country", MAX_COUNTRY_LEN)
    _validate_keywords(payload.get("keywords"))


def _validate_text_field(payload: dict[str, Any], field: str, max_len: int) -> None:
    value = payload.get(field)
    if not isinstance(value, str):
        raise SummaryValidationError(f"{field} must be a string.")
    if len(value) > max_len:
        raise SummaryValidationError(
            f"{field} exceeds max length {max_len} (got {len(value)})."
        )
    if "```" in value:
        raise SummaryValidationError(f"{field} contains Markdown code fences.")


def _validate_keywords(keywords: Any) -> None:
    if not isinstance(keywords, list):
        raise SummaryValidationError("keywords must be a JSON array of strings.")
    if not (3 <= len(keywords) <= MAX_KEYWORDS):
        raise SummaryValidationError(
            f"keywords must contain 3-{MAX_KEYWORDS} items (got {len(keywords)})."
        )
    for keyword in keywords:
        if not isinstance(keyword, str):
            raise SummaryValidationError("keywords must be strings.")
        if len(keyword) > MAX_KEYWORD_LEN:
            raise SummaryValidationError(
                f"keyword '{keyword}' exceeds max length {MAX_KEYWORD_LEN}."
            )
        if "```" in keyword:
            raise SummaryValidationError("keywords contain Markdown code fences.")


def save_summary_json(summary: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
