import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def write_report(
    path: Path,
    event: Dict[str, Any],
    result: Dict[str, Any],
) -> Dict[str, Any]:
    """Append a guard event report.

    Returns the report payload.
    """
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "guard": result,
    }
    line = json.dumps(payload, separators=(",", ":"))
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return {"path": str(path), "status": "ok"}


def load_reports(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    if not path.exists():
        return records
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records
