from __future__ import annotations

import json
import pathlib
from datetime import datetime
from typing import List

from pipeline.models import PaperSummary


def _render_paper(paper: PaperSummary) -> str:
    authors = ", ".join(paper.authors) if paper.authors else "(待补充)"
    affiliations = "; ".join(paper.affiliations) if paper.affiliations else "(待补充)"
    return "\n".join(
        [
            f"### {paper.title}",
            f"- 期刊：{paper.journal}",
            f"- 英文标题：{paper.title_en}",
            f"- 中文标题：{paper.title_zh}",
            f"- 作者：{authors}",
            f"- 单位：{affiliations}",
            f"- 日期：{paper.date}",
            f"- 原文链接：{paper.link}",
            "",
            "**摘要**",
            paper.abstract or "(暂无摘要)",
            "",
        ]
    )


def render(summary_path: pathlib.Path, output_dir: pathlib.Path) -> pathlib.Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    summaries_data = json.loads(summary_path.read_text(encoding="utf-8"))
    papers: List[PaperSummary] = [PaperSummary.from_dict(item) for item in summaries_data]

    date_stamp = datetime.utcnow().strftime("%Y%m%d")
    output_path = output_dir / f"papers_{date_stamp}.md"
    header = "# Nature / Science 论文摘要\n"
    body = "\n".join(_render_paper(paper) for paper in papers)
    output_path.write_text(f"{header}\n{body}", encoding="utf-8")
    return output_path
