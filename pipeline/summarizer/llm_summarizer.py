from __future__ import annotations

import json
import pathlib
from datetime import datetime
from typing import List

from pipeline.models import PaperSummary


def _heuristic_summary(title: str, description: str) -> str:
    if description:
        return description
    return f"This paper discusses {title}."


def summarize(raw_path: pathlib.Path, output_dir: pathlib.Path) -> pathlib.Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_items = json.loads(raw_path.read_text(encoding="utf-8"))

    summaries: List[PaperSummary] = []
    for item in raw_items:
        title = item.get("title", "")
        description = item.get("description", "")
        pub_date = item.get("pub_date") or datetime.utcnow().date().isoformat()
        summary = PaperSummary(
            journal=item.get("journal", ""),
            title=title,
            title_en=title,
            title_zh=title,
            authors=[],
            affiliations=[],
            abstract=_heuristic_summary(title, description),
            link=item.get("link", ""),
            date=pub_date,
        )
        summaries.append(summary)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_path = output_dir / f"summary_{timestamp}.json"
    output_path.write_text(
        json.dumps([s.to_dict() for s in summaries], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output_path
