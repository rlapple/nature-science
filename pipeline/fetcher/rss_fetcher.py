from __future__ import annotations

import json
import pathlib
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List


FEEDS = {
    "Nature": "https://www.nature.com/nature.rss",
    "Science": "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science",
}


def _fetch_feed(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")


def _parse_items(journal: str, xml_text: str) -> List[Dict[str, str]]:
    root = ET.fromstring(xml_text)
    items: List[Dict[str, str]] = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        items.append(
            {
                "journal": journal,
                "title": title,
                "link": link,
                "description": description,
                "pub_date": pub_date,
            }
        )
    return items


def fetch_latest(output_dir: pathlib.Path) -> pathlib.Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    all_items: List[Dict[str, str]] = []

    for journal, url in FEEDS.items():
        xml_text = _fetch_feed(url)
        all_items.extend(_parse_items(journal, xml_text))

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_path = output_dir / f"rss_{timestamp}.json"
    output_path.write_text(
        json.dumps(all_items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output_path
