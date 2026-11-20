"""Command line: ``consilience-judges ground FILE``.

FILE holds one JSON object per line:
    {"explanation": "...", "segments": {"response": "...", "policy": "..."}, "spans": [...]}

Segment order in the object is the priority order; the first segment is the judged text.
One grounding record is printed per line. Exit codes: 0 every cited phrase is in the
input, 1 at least one is not (or a span does not match), 2 usage or input error.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import METHOD_VERSION, __version__
from .guardrail import ground_output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="consilience-judges",
        description="Is the evidence a guardrail judge cites really in what it was given? No model, no network.",
    )
    parser.add_argument("--version", action="version", version=f"consilience-judges {__version__} ({METHOD_VERSION})")
    sub = parser.add_subparsers(dest="command", required=True)
    ground = sub.add_parser("ground", help="ground the verdicts in a JSON-lines file")
    ground.add_argument("file")
    ground.add_argument("--strict", action="store_true", help="exact case and quote style")
    args = parser.parse_args(argv)

    flagged = False
    try:
        with open(args.file, encoding="utf-8") as handle:
            lines = [line for line in handle if line.strip()]
    except OSError as exc:
        print(f"error: cannot read {args.file}: {exc.strerror}", file=sys.stderr)
        return 2
    for number, line in enumerate(lines, 1):
        try:
            item = json.loads(line)
            segments = list(item["segments"].items())
            record = ground_output(item, segments, lenient=not args.strict)
        except (ValueError, KeyError, AttributeError, TypeError) as exc:
            print(f"error: line {number}: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 2
        bad_span = any(span["result"] in ("MISMATCH", "OUT_OF_RANGE") for span in record.get("spans", []))
        flagged = flagged or record["not_in_input"] > 0 or bad_span
        sys.stdout.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
    return 1 if flagged else 0


if __name__ == "__main__":
    raise SystemExit(main())
