"""
Convert GAME_EXPLAINED.md to DOCX using Pandoc.

Pandoc preserves tables, code blocks, headings, and lists much better than a
manual line-by-line writer, so it is the preferred conversion path for this
project.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parent


def convert_markdown_to_docx(input_name: str, output_name: str) -> None:
    input_path = WORKSPACE / input_name
    output_path = WORKSPACE / output_name

    command = [
        "pandoc",
        str(input_path),
        "-o",
        str(output_path),
        "--from",
        "markdown",
        "--to",
        "docx",
        "--wrap=none",
    ]

    subprocess.run(command, check=True)
    print(f"Created {output_path}")


if __name__ == "__main__":
    convert_markdown_to_docx("GAME_EXPLAINED.md", "GAME_EXPLAINED.docx")
