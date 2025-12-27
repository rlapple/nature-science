#!/usr/bin/env python3
import argparse
import json
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


REQUIRED_FIELDS = {
    "discipline_zh",
    "discipline_en",
    "paper_id",
    "title_en",
    "title_zh",
    "abstract_zh",
    "url",
}


def _resolve_date(summary_data: dict) -> str:
    if "date" in summary_data and summary_data["date"]:
        return str(summary_data["date"])
    if summary_data.get("papers"):
        first_date = summary_data["papers"][0].get("date")
        if first_date:
            return str(first_date)
    return date.today().isoformat()


def _normalize_paper(paper: dict) -> dict:
    normalized = dict(paper)
    if "paper_id" not in normalized and "id" in normalized:
        normalized["paper_id"] = normalized["id"]
    missing = REQUIRED_FIELDS - normalized.keys()
    if missing:
        raise ValueError(f"Paper missing required fields: {sorted(missing)}")
    return normalized


def render_markdown(summary_path: Path, output_root: Path, template_path: Path) -> list[Path]:
    with summary_path.open("r", encoding="utf-8") as handle:
        summary_data = json.load(handle)

    papers = summary_data.get("papers")
    if not papers:
        raise ValueError("summary.json must include a non-empty 'papers' list")

    report_date = _resolve_date(summary_data)
    output_dir = output_root / report_date
    output_dir.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(enabled_extensions=("md",)),
    )
    template = env.get_template(template_path.name)

    outputs = []
    for paper in papers:
        normalized = _normalize_paper(paper)
        content = template.render(**normalized)
        output_path = output_dir / f"{normalized['paper_id']}.md"
        output_path.write_text(content, encoding="utf-8")
        outputs.append(output_path)

    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Render markdown files from summary.json")
    parser.add_argument("--input", default="summary.json", help="Path to summary.json")
    parser.add_argument(
        "--output-dir",
        default="data/md",
        help="Root directory for markdown output",
    )
    parser.add_argument(
        "--template",
        default="pipeline/renderer/templates/paper.md",
        help="Path to the markdown template",
    )
    args = parser.parse_args()

    summary_path = Path(args.input)
    output_root = Path(args.output_dir)
    template_path = Path(args.template)

    outputs = render_markdown(summary_path, output_root, template_path)
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
