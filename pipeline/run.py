from __future__ import annotations

import argparse
import pathlib

from pipeline.exporter.pdf_exporter import export
from pipeline.fetcher.rss_fetcher import fetch_latest
from pipeline.renderer.markdown_renderer import render
from pipeline.summarizer.llm_summarizer import summarize


BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
SUMMARY_DIR = DATA_DIR / "summary"
MD_DIR = DATA_DIR / "md"
PDF_DIR = BASE_DIR / "public" / "pdfs"


def run_pipeline() -> None:
    raw_path = fetch_latest(RAW_DIR)
    summary_path = summarize(raw_path, SUMMARY_DIR)
    md_path = render(summary_path, MD_DIR)
    export(md_path, PDF_DIR)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nature/Science pipeline runner")
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Skip PDF export step (Markdown only)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_path = fetch_latest(RAW_DIR)
    summary_path = summarize(raw_path, SUMMARY_DIR)
    md_path = render(summary_path, MD_DIR)

    if not args.skip_pdf:
        export(md_path, PDF_DIR)


if __name__ == "__main__":
    main()
