from pathlib import Path
import json

SCHEMA_PATH = Path(__file__).with_suffix(".json")
with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    SCHEMA = json.load(f)

__all__ = ["SCHEMA", "SCHEMA_PATH"]
