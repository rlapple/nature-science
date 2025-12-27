#!/usr/bin/env bash
set -euo pipefail

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc is required but not installed." >&2
  exit 1
fi

if ! command -v xelatex >/dev/null 2>&1; then
  echo "xelatex is required but not installed." >&2
  exit 1
fi

if [ $# -lt 1 ]; then
  echo "Usage: $0 <input.md> [version-tag]" >&2
  exit 1
fi

INPUT_MD="$1"
VERSION_TAG="${2:-}"

if [ ! -f "$INPUT_MD" ]; then
  echo "Input file not found: $INPUT_MD" >&2
  exit 1
fi

BASENAME="$(basename "$INPUT_MD" .md)"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

if [ -n "$VERSION_TAG" ]; then
  OUTPUT_NAME="${BASENAME}-${VERSION_TAG}.pdf"
else
  OUTPUT_NAME="${BASENAME}-${TIMESTAMP}.pdf"
fi

OUTPUT_DIR="$(cd "$(dirname "$0")/../../public/pdfs" && pwd)"
OUTPUT_PDF="$OUTPUT_DIR/$OUTPUT_NAME"

pandoc "$INPUT_MD" \
  -o "$OUTPUT_PDF" \
  --pdf-engine=xelatex \
  -V mainfont="Noto Sans CJK SC" \
  -V CJKmainfont="Noto Sans CJK SC"

echo "Generated: $OUTPUT_PDF"
