import json
from pathlib import Path

required = {"date", "sport", "matchup", "market", "pick", "confidence", "edge", "tier"}
path = Path(__file__).resolve().parents[1] / "data" / "todays_picks.json"
items = json.loads(path.read_text())
for i, item in enumerate(items, start=1):
    missing = required - set(item)
    if missing:
        raise ValueError(f"Pick {i} missing fields: {sorted(missing)}")
print(f"Validated {len(items)} picks.")
