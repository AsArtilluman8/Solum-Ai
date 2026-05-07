#!/usr/bin/env python3
"""Solum-AI Stage 2 eval runner.

This script intentionally has no third-party dependencies. It supports the
small Stage 1 YAML shape used in eval/*/tasks.yaml and can generate manual
scoring templates and Markdown reports.

Usage:
  python tools/eval_runner.py list
  python tools/eval_runner.py export --run-id local-test-001 --model "Solum prompt v0" --out eval/runs/local-test-001.yaml
  python tools/eval_runner.py report --results eval/runs/local-test-001.yaml --out eval/runs/local-test-001.md
"""

from __future__ import annotations

import argparse
import datetime as _dt
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "eval"
TASK_FILES = [
    EVAL_DIR / "discipline" / "tasks.yaml",
    EVAL_DIR / "coding" / "tasks.yaml",
    EVAL_DIR / "verification" / "tasks.yaml",
]


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in {"[]", "null", "None"}:
        return [] if value == "[]" else None
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_strip_quotes(part.strip()) for part in inner.split(",")]
    if value.isdigit():
        return int(value)
    return _strip_quotes(value)


def load_stage1_tasks(path: pathlib.Path) -> list[dict[str, Any]]:
    """Parse the limited YAML shape used by Stage 1 task files.

    This is not a general YAML parser. It is enough for the repository's current
    task files and avoids requiring PyYAML on small/mobile environments.
    """
    if not path.exists():
        raise FileNotFoundError(path)

    lines = path.read_text(encoding="utf-8").splitlines()
    tasks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    active_key: str | None = None
    active_indent: int | None = None
    block_lines: list[str] = []
    list_key: str | None = None

    def flush_block() -> None:
        nonlocal active_key, active_indent, block_lines
        if current is not None and active_key is not None:
            # Remove one common indentation level from block lines.
            non_empty = [ln for ln in block_lines if ln.strip()]
            if non_empty:
                min_indent = min(len(ln) - len(ln.lstrip(" ")) for ln in non_empty)
                text = "\n".join(ln[min_indent:] if len(ln) >= min_indent else ln for ln in block_lines).rstrip()
            else:
                text = ""
            current[active_key] = text
        active_key = None
        active_indent = None
        block_lines = []

    for raw in lines:
        if not raw.strip() or raw.strip().startswith("#"):
            if active_key is not None:
                block_lines.append("")
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()

        if active_key is not None:
            if indent > (active_indent or 0):
                block_lines.append(raw)
                continue
            flush_block()

        if stripped == "tasks:":
            continue

        if stripped.startswith("- id:"):
            if current is not None:
                tasks.append(current)
            current = {"id": _parse_scalar(stripped.split(":", 1)[1])}
            list_key = None
            continue

        if current is None:
            continue

        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:\s*\|\s*$", stripped):
            key = stripped.split(":", 1)[0]
            active_key = key
            active_indent = indent
            block_lines = []
            list_key = None
            continue

        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:\s*$", stripped):
            key = stripped[:-1]
            current[key] = []
            list_key = key
            continue

        if stripped.startswith("- ") and list_key:
            current.setdefault(list_key, []).append(_parse_scalar(stripped[2:]))
            continue

        if ":" in stripped:
            key, value = stripped.split(":", 1)
            current[key.strip()] = _parse_scalar(value)
            list_key = None

    flush_block()
    if current is not None:
        tasks.append(current)

    return tasks


def load_all_tasks() -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for path in TASK_FILES:
        tasks.extend(load_stage1_tasks(path))
    return tasks


def cmd_list(_: argparse.Namespace) -> int:
    tasks = load_all_tasks()
    print(f"Loaded {len(tasks)} tasks")
    for task in tasks:
        print(f"- {task.get('id')} [{task.get('category')}]: {task.get('title')}")
    return 0


def _yaml_block(text: str, indent: int = 4) -> str:
    pad = " " * indent
    if not text:
        return f"|\n{pad}"
    return "|\n" + "\n".join(f"{pad}{line}" for line in text.splitlines())


def cmd_export(args: argparse.Namespace) -> int:
    tasks = load_all_tasks()
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    date = _dt.date.today().isoformat()

    lines: list[str] = []
    lines.append("run:")
    lines.append(f"  id: {args.run_id}")
    lines.append(f"  date: {date}")
    lines.append("  evaluator: manual")
    lines.append(f"  model_or_prompt: {args.model}")
    lines.append("  notes: \"\"")
    lines.append("")
    lines.append("results:")

    for task in tasks:
        lines.append(f"  - task_id: {task.get('id')}")
        lines.append(f"    category: {task.get('category')}")
        lines.append(f"    title: {_quote(task.get('title', ''))}")
        lines.append("    prompt: " + _yaml_block(str(task.get("prompt", "")), indent=6))
        lines.append("    score: null")
        lines.append("    failure_tags: []")
        lines.append("    notes: \"\"")
        lines.append("")

    lines.append("summary:")
    lines.append(f"  total_tasks: {len(tasks)}")
    lines.append(f"  max_score: {len(tasks) * 2}")
    lines.append("  actual_score: 0")
    lines.append("  pass_rate_percent: 0")
    lines.append("  key_failures: []")
    lines.append("  release_recommendation: experimental_only")

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote manual scoring template: {out}")
    return 0


def _quote(value: Any) -> str:
    text = str(value).replace('"', '\\"')
    return f'"{text}"'


def _extract_scores(results_text: str) -> list[int]:
    scores: list[int] = []
    for match in re.finditer(r"^\s*score:\s*(\d+)\s*$", results_text, flags=re.MULTILINE):
        value = int(match.group(1))
        if value not in {0, 1, 2}:
            raise ValueError(f"Invalid score {value}; expected 0, 1, or 2")
        scores.append(value)
    return scores


def _extract_run_field(results_text: str, field: str, default: str = "unknown") -> str:
    match = re.search(rf"^\s*{re.escape(field)}:\s*(.+?)\s*$", results_text, flags=re.MULTILINE)
    if not match:
        return default
    return _strip_quotes(match.group(1))


def cmd_report(args: argparse.Namespace) -> int:
    results_path = pathlib.Path(args.results)
    if not results_path.exists():
        raise FileNotFoundError(results_path)
    text = results_path.read_text(encoding="utf-8")
    scores = _extract_scores(text)
    tasks = load_all_tasks()
    max_score = len(tasks) * 2
    actual = sum(scores)
    percent = round((actual / max_score) * 100, 2) if max_score else 0

    run_id = _extract_run_field(text, "id", results_path.stem)
    model = _extract_run_field(text, "model_or_prompt", "unknown")
    date = _extract_run_field(text, "date", _dt.date.today().isoformat())

    report = [
        f"# Solum-AI Eval Report: {run_id}",
        "",
        f"Date: {date}",
        f"Model/prompt: {model}",
        "",
        "## Summary",
        "",
        f"- Tasks: {len(tasks)}",
        f"- Scored answers: {len(scores)}",
        f"- Score: {actual}/{max_score}",
        f"- Pass rate: {percent}%",
        "",
        "## Interpretation",
        "",
    ]

    if len(scores) < len(tasks):
        report.append("This run is incomplete: not all tasks have numeric scores.")
    elif percent >= 80:
        report.append("Strong result for this small Stage 1 benchmark. Still experimental until repeated.")
    elif percent >= 60:
        report.append("Partial result. Useful, but failure cases need review before any stable claim.")
    else:
        report.append("Weak result. Keep as experimental only and inspect failure patterns.")

    report.extend([
        "",
        "## Next checks",
        "",
        "- Review all score 0 tasks.",
        "- Identify repeated failure tags.",
        "- Compare against at least one baseline prompt/model.",
        "- Do not mark any prompt/model stable from a single run.",
        "",
    ])

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report), encoding="utf-8")
    print(f"Wrote report: {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Solum-AI Stage 2 eval runner")
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list", help="List available eval tasks")
    list_cmd.set_defaults(func=cmd_list)

    export_cmd = sub.add_parser("export", help="Export manual scoring template")
    export_cmd.add_argument("--run-id", required=True)
    export_cmd.add_argument("--model", required=True)
    export_cmd.add_argument("--out", required=True)
    export_cmd.set_defaults(func=cmd_export)

    report_cmd = sub.add_parser("report", help="Generate Markdown report from scored YAML")
    report_cmd.add_argument("--results", required=True)
    report_cmd.add_argument("--out", required=True)
    report_cmd.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - CLI should print concise failure.
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
