"""BetLabIQ starter prediction updater.

Replace the sample model section with your real model logic.
This script is designed to be run by GitHub Actions and write JSON files
that the GitHub Pages website can read.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(exist_ok=True)

TODAY = date.today().isoformat()

# TODO: Replace with API pulls + your actual model features.
picks = [
    {
        "date": TODAY,
        "sport": "MLB",
        "league": "MLB",
        "matchup": "Sample Team A vs Sample Team B",
        "start_time": "7:10 PM ET",
        "market": "Moneyline",
        "pick": "Sample Team A ML",
        "odds": "-125",
        "model_probability": 60.5,
        "implied_probability": 55.6,
        "edge": 4.9,
        "confidence": 69,
        "tier": "Medium",
        "is_premium": False,
        "reason_1": "Starter rating advantage",
        "reason_2": "Bullpen rest edge",
        "reason_3": "Recent run creation trend",
    }
]

with (DATA_DIR / "todays_picks.json").open("w", encoding="utf-8") as f:
    json.dump(picks, f, indent=2)

status = {"last_updated": TODAY, "picks_written": len(picks)}
with (DATA_DIR / "site_status.json").open("w", encoding="utf-8") as f:
    json.dump(status, f, indent=2)

print(f"Wrote {len(picks)} picks for {TODAY}")
