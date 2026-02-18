#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


TEMPLATES = {
    "analysis.md": """# Analysis

- Ticket: {ticket}
- Created At: {created_at}

## Scope


## Code Boundaries


## Risk Map

- High:
- Medium:
- Low:

## Refactor Targets


## Out of Scope


""",
    "preserve.md": """# Preserve

- Ticket: {ticket}
- Created At: {created_at}

## Existing Test Baseline


## Added Characterization Tests


## Snapshot / Baseline Artifacts


## Safety-Net Gaps


""",
    "improve-log.md": """# Improve Log

- Ticket: {ticket}
- Created At: {created_at}

## Step Log

### Step 1

- Change:
- Why:
- Validation Command:
- Result:
- Rollback Needed:

""",
    "validation.md": """# Validation

- Ticket: {ticket}
- Created At: {created_at}

## Behavior Checks


## Test Results


## Performance Guardrail


## Regression Findings


""",
    "summary.md": """# Summary

- Ticket: {ticket}
- Created At: {created_at}

## Structural Improvements


## Preserved Behaviors


## Known Limitations


## Next Safe Slice


""",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize DDD refactor artifact files"
    )
    parser.add_argument("--ticket", required=True, help="ticket or task identifier")
    parser.add_argument(
        "--base-dir",
        default=".refactor",
        help="base directory for artifacts (default: .refactor)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="overwrite files if they already exist",
    )
    return parser.parse_args()


def write_file(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return f"SKIP  {path} (already exists)"
    path.write_text(content, encoding="utf-8")
    return f"WRITE {path}"


def main() -> int:
    args = parse_args()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    ticket_dir = Path(args.base_dir).resolve() / args.ticket
    ticket_dir.mkdir(parents=True, exist_ok=True)

    print(f"Target: {ticket_dir}")
    for file_name, template in TEMPLATES.items():
        output_path = ticket_dir / file_name
        result = write_file(
            output_path,
            template.format(ticket=args.ticket, created_at=created_at),
            args.force,
        )
        print(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
