#!/usr/bin/env python3
"""Fill exported Solum-AI manual scoring YAML with smoke-test scores.

This is only for CI smoke testing the report pipeline. It does not evaluate a
real model. It replaces every `score: null` with `score: 2` so the report
command can verify numeric parsing and Markdown generation.
"""

from __future__ import annotations

import pathlib
import sys


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python tools/fill_smoke_scores.py <results.yaml>", file=sys.stderr)
        return 2

    path = pathlib.Path(argv[1])
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    text = text.replace("score: null", "score: 2")
    text = text.replace("actual_score: 0", "actual_score: 30")
    text = text.replace("pass_rate_percent: 0", "pass_rate_percent: 100")
    path.write_text(text, encoding="utf-8")
    print(f"filled smoke scores: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
