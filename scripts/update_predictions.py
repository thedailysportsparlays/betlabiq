import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

today = datetime.utcnow().strftime("%Y-%m-%d")

picks = [
    {
        "date": today,
        "sport": "MLB",
        "league": "MLB",
        "matchup": "Today's MLB Game 1",
        "start_time": "TBD",
        "market": "Game Preview",
        "pick": "Model Pending",
        "odds": "TBD",
        "model_probability": 0,
        "implied_probability": 0,
        "edge": 0,
        "confidence": 0,
        "tier": "Lean",
        "is_premium": False,
        "reason_1": "Daily slate refreshed",
        "reason_2": "Awaiting model inputs",
        "reason_3": "Pick updates after analysis"
    }
]

with open(DATA_DIR / "todays_picks.json", "w") as f:
    json.dump(picks, f, indent=2)

print(f"Updated {DATA_DIR / 'todays_picks.json'}")
