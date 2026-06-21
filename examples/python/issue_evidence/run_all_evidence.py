#!/usr/bin/env python3
"""Run all security issue repros and write cropped evidence PNGs + logs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
OUT = ROOT / "output"

SCRIPTS = {
    "3235": REPO / "examples/python/repro_delete_data_missing_row.py",
    "3237": ROOT / "repro_3237_ssrf.py",
    "3238": ROOT / "repro_3238_local_file.py",
    "3239": ROOT / "repro_3239_cypher.py",
    "3240": ROOT / "repro_3240_exception_leak.py",
    "3241": ROOT / "repro_3241_superuser.py",
}


def _clean_output(text: str) -> str:
    keep = []
    for line in text.splitlines():
        if any(
            token in line
            for token in (
                "\x1b[",
                "executing functools",
                "operation functools",
                "connect_tcp",
                "start_tls",
                "send_request",
                "receive_response",
                "response_closed",
                "close.started",
                "close.complete",
                "packages.unstructured.io",
                "Using selector:",
                "debug    ",
            )
        ):
            continue
        keep.append(line)
    return "\n".join(keep[-20:])


def run_one(issue: str, script: Path) -> tuple[int, str]:
    header = f"$ uv run python {script.relative_to(REPO)}\n"
    proc = subprocess.run(
        ["uv", "run", "python", str(script)],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    body = (proc.stdout or "") + (proc.stderr or "")
    cleaned = _clean_output(body)
    output = header + cleaned
    if proc.returncode != 0:
        output += f"\n[exit code {proc.returncode}]"
    return proc.returncode, output


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from generate_evidence_images import text_to_png

    OUT.mkdir(parents=True, exist_ok=True)
    failures = []

    for issue, script in SCRIPTS.items():
        code, text = run_one(issue, script)
        log_path = OUT / f"issue-{issue}.log"
        png_path = OUT / f"issue-{issue}-evidence.png"
        log_path.write_text(text, encoding="utf-8")
        text_to_png(text, png_path)
        print(f"Issue #{issue}: exit={code} -> {png_path}")
        if code != 0:
            failures.append(issue)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
