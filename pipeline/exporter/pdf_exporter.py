from __future__ import annotations

import pathlib
import shutil
import subprocess
from datetime import datetime


def export(markdown_path: pathlib.Path, output_dir: pathlib.Path) -> pathlib.Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    if shutil.which("pandoc") is None:
        raise RuntimeError("Pandoc not found. Please install pandoc to export PDFs.")

    date_stamp = datetime.utcnow().strftime("%Y%m%d")
    output_path = output_dir / f"papers_{date_stamp}.pdf"
    subprocess.run(
        ["pandoc", str(markdown_path), "-o", str(output_path)],
        check=True,
    )
    return output_path
