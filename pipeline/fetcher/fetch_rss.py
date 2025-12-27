#!/usr/bin/env python3
import argparse
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

RSS_SOURCES = {
    "nature": {
        "nature": "https://www.nature.com/nature.rss",
        "biology": "https://www.nature.com/subjects/biology.rss",
        "chemistry": "https://www.nature.com/subjects/chemistry.rss",
        "physics": "https://www.nature.com/subjects/physics.rss",
    },
    "science": {
        "latest": "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science",
    },
}

DOI_PATTERN = re.compile(r"10\.\d{4,9}/[\w.()/:;<>-]+", re.IGNORECASE)


@dataclass
class RssItem:
    title: str
    link: str
    date: str
    doi: Optional[str] = None


NAMESPACES = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "prism": "http://prismstandard.org/namespaces/basic/2.0/",
    "atom": "http://www.w3.org/2005/Atom",
}


def fetch_xml(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read().decode("utf-8")


def extract_doi(*values: Optional[str]) -> Optional[str]:
    for value in values:
        if not value:
            continue
        match = DOI_PATTERN.search(value)
        if match:
            return match.group(0)
    return None


def normalize_date(value: Optional[str]) -> str:
    if not value:
        return ""
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(value, fmt).isoformat()
        except ValueError:
            continue
    return value


def parse_rss_items(xml_text: str) -> Iterable[RssItem]:
    root = ET.fromstring(xml_text)
    items = root.findall(".//item")
    if not items:
        items = root.findall(".//atom:entry", NAMESPACES)
    for item in items:
        title = (item.findtext("title") or item.findtext("atom:title", namespaces=NAMESPACES) or "").strip()
        link = item.findtext("link")
        if link is None:
            link_elem = item.find("atom:link", NAMESPACES)
            link = link_elem.get("href") if link_elem is not None else ""
        link = (link or "").strip()
        pub_date = (
            item.findtext("pubDate")
            or item.findtext("atom:updated", namespaces=NAMESPACES)
            or item.findtext("dc:date", namespaces=NAMESPACES)
            or ""
        )
        doi = extract_doi(
            item.findtext("prism:doi", namespaces=NAMESPACES),
            item.findtext("dc:identifier", namespaces=NAMESPACES),
            link,
            title,
        )
        yield RssItem(title=title, link=link, date=normalize_date(pub_date), doi=doi)


def dedupe_items(items: Iterable[RssItem]) -> list[RssItem]:
    seen: set[str] = set()
    unique: list[RssItem] = []
    for item in items:
        key = item.doi or item.link
        if not key:
            key = f"{item.title}-{item.date}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def parse_sources(names: Optional[list[str]]) -> dict[str, str]:
    if not names:
        selected = {
            f"nature-{label}": url for label, url in RSS_SOURCES["nature"].items()
        }
        selected.update({f"science-{label}": url for label, url in RSS_SOURCES["science"].items()})
        return selected

    resolved: dict[str, str] = {}
    for name in names:
        group, _, label = name.partition(":")
        if group in RSS_SOURCES and label:
            if label not in RSS_SOURCES[group]:
                raise ValueError(f"Unknown source label '{label}' for group '{group}'.")
            resolved[f"{group}-{label}"] = RSS_SOURCES[group][label]
        elif name in RSS_SOURCES:
            resolved.update({f"{name}-{label}": url for label, url in RSS_SOURCES[name].items()})
        else:
            raise ValueError(f"Unknown source '{name}'.")
    return resolved


def write_output(items: list[RssItem], output_path: Path) -> None:
    payload = [
        {"title": item.title, "link": item.link, "date": item.date}
        for item in items
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch and normalize RSS feeds from Nature and Science.")
    parser.add_argument("--limit", type=int, default=20, help="Number of latest items to keep per feed.")
    parser.add_argument(
        "--sources",
        nargs="*",
        help="Select sources (e.g. nature, science, nature:biology, science:latest). Defaults to all.",
    )
    parser.add_argument(
        "--output-dir",
        default="data/raw",
        help="Directory to write JSON outputs.",
    )
    args = parser.parse_args()

    try:
        sources = parse_sources(args.sources)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir)
    for name, url in sources.items():
        xml_text = fetch_xml(url)
        items = list(parse_rss_items(xml_text))
        unique_items = dedupe_items(items)[: args.limit]
        output_path = output_dir / f"{name}.json"
        write_output(unique_items, output_path)
        print(f"Wrote {len(unique_items)} items to {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
