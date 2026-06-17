import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data" / "raw" / "MLB_Prediction_Model.xlsx"
PUBLIC_DIR = BASE_DIR / "data" / "public"
EMAIL_DIR = BASE_DIR / "emails" / "generated"

PUBLIC_GAMES_JSON = PUBLIC_DIR / "public_games.json"
FREE_PICK_JSON = PUBLIC_DIR / "free_pick.json"
DAILY_EMAIL_MD = EMAIL_DIR / "daily_free_pick.md"

PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
EMAIL_DIR.mkdir(parents=True, exist_ok=True)


def safe_value(row, column, default=""):
    value = row.get(column, default)
    if pd.isna(value):
        return default
    return value


def probability_to_percent(value):
    value = float(value)
    if value <= 1:
        return round(value * 100, 1)
    return round(value, 1)


print(f"Looking for workbook at: {INPUT_FILE}")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Workbook not found. Expected file here: {INPUT_FILE}"
    )

daily_winners = pd.read_excel(INPUT_FILE, sheet_name="daily_winners")

print("daily_winners columns:")
print(list(daily_winners.columns))

required_columns = [
    "game_date",
    "game_time",
    "game",
    "moneyline_pick",
    "model_probability",
    "blowout_score",
    "confidence",
    "key_reason_1",
    "key_reason_2",
    "risk_flag"
]

missing = [col for col in required_columns if col not in daily_winners.columns]

if missing:
    raise ValueError(f"Missing required columns in daily_winners tab: {missing}")

daily_winners["model_probability"] = pd.to_numeric(
    daily_winners["model_probability"],
    errors="coerce"
)

daily_winners["blowout_score"] = pd.to_numeric(
    daily_winners["blowout_score"],
    errors="coerce"
)

daily_winners = daily_winners.dropna(subset=["model_probability", "blowout_score"])

if daily_winners.empty:
    raise ValueError("No usable rows found after cleaning model_probability and blowout_score.")

# Public website games: show games, but do NOT reveal picks.
public_games = []

for _, row in daily_winners.iterrows():
    public_games.append({
        "date": str(safe_value(row, "game_date", "")),
        "sport": "MLB",
        "matchup": str(safe_value(row, "game", "")),
        "game_time": str(safe_value(row, "game_time", "")),
        "status": "Model reviewed",
        "public_label": "Pick available by email",
        "is_premium_locked": True
    })

with open(PUBLIC_GAMES_JSON, "w", encoding="utf-8") as f:
    json.dump(public_games, f, indent=2)


# Free pick rule:
# Highest model_probability
# AND blowout_score > 3 OR blowout_score < -3

eligible_picks = daily_winners[
    (daily_winners["blowout_score"] > 3) |
    (daily_winners["blowout_score"] < -3)
].copy()

if eligible_picks.empty:
    raise ValueError(
        "No eligible free pick found. Need blowout_score > 3 or blowout_score < -3."
    )

eligible_picks = eligible_picks.sort_values(
    "model_probability",
    ascending=False
)

top_pick = eligible_picks.iloc[0]

confidence_percent = probability_to_percent(
    safe_value(top_pick, "model_probability", 0)
)

free_pick = {
    "date": str(safe_value(top_pick, "game_date", "")),
    "sport": "MLB",
    "matchup": str(safe_value(top_pick, "game", "")),
    "game_time": str(safe_value(top_pick, "game_time", "")),
    "pick": str(safe_value(top_pick, "moneyline_pick", "")),
    "market": "Moneyline",
    "odds": "TBD",
    "confidence": confidence_percent,
    "tier": str(safe_value(top_pick, "confidence", "Model Pick")),
    "reason_1": str(safe_value(top_pick, "key_reason_1", "Model edge")),
    "reason_2": str(safe_value(top_pick, "key_reason_2", "Matchup advantage")),
    "reason_3": "Highest model probability among qualifying blowout-score plays",
    "risk": str(safe_value(top_pick, "risk_flag", "Monitor line movement and confirmed lineups.")),
    "blowout_score": round(float(safe_value(top_pick, "blowout_score", 0)), 3),
    "email_subject": f"🎯 BetLabIQ Game of the Day | {safe_value(top_pick, 'game', 'MLB')}"
}

with open(FREE_PICK_JSON, "w", encoding="utf-8") as f:
    json.dump(free_pick, f, indent=2)


email_body = f"""# 🎯 GAME OF THE DAY

## {free_pick["matchup"]}

**Game Time:** {free_pick["game_time"]}

---

## BETLABIQ PICK

# {free_pick["pick"]}

**Confidence:** {free_pick["confidence"]}/100  
**Tier:** {free_pick["tier"]}

---

## Why We Like It

✓ {free_pick["reason_1"]}

✓ {free_pick["reason_2"]}

✓ {free_pick["reason_3"]}

---

## Biggest Risk

{free_pick["risk"]}

---

No fake locks. No guarantees. Just one game we believe offers value today.

— BetLabIQ
"""

with open(DAILY_EMAIL_MD, "w", encoding="utf-8") as f:
    f.write(email_body)

print("Created public games JSON:", PUBLIC_GAMES_JSON)
print("Created free pick JSON:", FREE_PICK_JSON)
print("Created Beehiiv email draft:", DAILY_EMAIL_MD)
print("Selected free pick:", free_pick["pick"])
