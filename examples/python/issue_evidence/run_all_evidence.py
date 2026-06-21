#!/usr/bin/env python3
"""Run live CLI repro sessions and write terminal transcripts + evidence PNGs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
OUT = ROOT / "output"

# Each block is executed live in bash. Commands must print evidence to stdout.
EVIDENCE_BLOCKS: dict[str, str] = {
    "3235": r"""
set -euo pipefail
export TELEMETRY_DISABLED=1
cd "{repo}"

echo '$ sed -n "167,176p" cognee/api/v1/datasets/datasets.py'
sed -n '167,176p' cognee/api/v1/datasets/datasets.py
echo
echo '$ uv run python examples/python/repro_delete_data_missing_row.py'
uv run python examples/python/repro_delete_data_missing_row.py 2>/dev/null
printf '\n[exit code: %s]\n' $?
""",
    "3237": r"""
set -euo pipefail
export TELEMETRY_DISABLED=1
cd "{repo}"

echo '$ rg -n ALLOW_HTTP_REQUESTS cognee --glob "*.py"'
if command -v rg >/dev/null 2>&1; then
  rg -n ALLOW_HTTP_REQUESTS cognee --glob "*.py"
else
  grep -rn ALLOW_HTTP_REQUESTS cognee --include='*.py'
fi
echo
echo '$ sed -n "61,63p" cognee/tasks/ingestion/save_data_item_to_storage.py'
sed -n '61,63p' cognee/tasks/ingestion/save_data_item_to_storage.py
echo
echo '$ ALLOW_HTTP_REQUESTS=false uv run python examples/python/issue_evidence/repro_3237_ssrf.py'
ALLOW_HTTP_REQUESTS=false uv run python examples/python/issue_evidence/repro_3237_ssrf.py 2>/dev/null
printf '\n[exit code: %s]\n' $?
""",
    "3238": r"""
set -euo pipefail
export TELEMETRY_DISABLED=1
cd "{repo}"

echo '$ sed -n "65,67p" cognee/tasks/ingestion/save_data_item_to_storage.py'
sed -n '65,67p' cognee/tasks/ingestion/save_data_item_to_storage.py
echo
echo '$ uv run python examples/python/issue_evidence/repro_3238_local_file.py'
uv run python examples/python/issue_evidence/repro_3238_local_file.py 2>/dev/null
printf '\n[exit code: %s]\n' $?
""",
    "3239": r"""
set -euo pipefail
export TELEMETRY_DISABLED=1
cd "{repo}"

echo '$ rg -n "ALLOW_CYPHER_QUERY" cognee/modules/search/methods/get_search_type_retriever_instance.py'
if command -v rg >/dev/null 2>&1; then
  rg -n "ALLOW_CYPHER_QUERY" cognee/modules/search/methods/get_search_type_retriever_instance.py
else
  grep -n "ALLOW_CYPHER_QUERY" cognee/modules/search/methods/get_search_type_retriever_instance.py
fi
echo
echo '$ uv run python examples/python/issue_evidence/repro_3239_cypher.py'
uv run python examples/python/issue_evidence/repro_3239_cypher.py 2>/dev/null
printf '\n[exit code: %s]\n' $?
""",
    "3240": r"""
set -uo pipefail
export TELEMETRY_DISABLED=1
cd "{repo}"

echo '$ grep -n "detail=str(error)" cognee/api/v1/add/routers/get_add_router.py'
grep -n "detail=str(error)" cognee/api/v1/add/routers/get_add_router.py
echo
echo '$ uv run python examples/python/issue_evidence/repro_3240_exception_leak.py 2>&1 | tail -8'
uv run python examples/python/issue_evidence/repro_3240_exception_leak.py 2>&1 | tail -8
printf '\n[exit code: %s]\n' $?
""",
    "3241": r"""
set -euo pipefail
export TELEMETRY_DISABLED=1
cd "{repo}"

echo '$ rg -n "get_authenticated_user|is_superuser|ENABLE_BACKEND_ACCESS_CONTROL" cognee/modules/users/methods/get_authenticated_user.py | head -8'
if command -v rg >/dev/null 2>&1; then
  rg -n "get_authenticated_user|is_superuser|ENABLE_BACKEND_ACCESS_CONTROL" cognee/modules/users/methods/get_authenticated_user.py | head -8
else
  grep -En "get_authenticated_user|is_superuser|ENABLE_BACKEND_ACCESS_CONTROL" cognee/modules/users/methods/get_authenticated_user.py | head -8
fi
echo
echo '$ ENABLE_BACKEND_ACCESS_CONTROL=false uv run python examples/python/issue_evidence/repro_3241_superuser.py'
ENABLE_BACKEND_ACCESS_CONTROL=false uv run python examples/python/issue_evidence/repro_3241_superuser.py 2>/dev/null
printf '\n[exit code: %s]\n' $?
""",
}


def run_block(issue: str, script: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["bash", "-lc", script],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    transcript = proc.stdout
    if proc.stderr.strip():
        transcript = f"{transcript.rstrip()}\n\n# stderr\n{proc.stderr.rstrip()}\n"
    if proc.returncode != 0:
        transcript = f"{transcript.rstrip()}\n[exit code: {proc.returncode}]\n"
    return proc.returncode, transcript


def main() -> int:
    sys.path.insert(0, str(ROOT))
    from generate_evidence_images import strip_ansi, text_to_png

    OUT.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    for issue, template in EVIDENCE_BLOCKS.items():
        script = template.format(repo=REPO)
        code, transcript = run_block(issue, script)
        clean = strip_ansi(transcript)

        txt_path = OUT / f"issue-{issue}-transcript.txt"
        log_path = OUT / f"issue-{issue}.log"
        png_path = OUT / f"issue-{issue}-evidence.png"

        txt_path.write_text(clean, encoding="utf-8")
        log_path.write_text(clean, encoding="utf-8")
        text_to_png(clean, png_path)

        print(f"Issue #{issue}: exit={code} -> {png_path}")
        if code != 0:
            failures.append(issue)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
