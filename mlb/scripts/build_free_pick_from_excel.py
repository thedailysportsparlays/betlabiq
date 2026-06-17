import json
from pathlib import Path

import pandas as pd


# ==============================
# File Paths
# ==============================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data" / "raw" / "MLB_Prediction_Model.xlsx"
PUBLIC_DIR = BASE_DIR / "data" / "public"
EMAIL_DIR = BASE_DIR / "emails" / "generated"

FREE_PICK_JSON = PUBLIC_DIR / "free_pick.json"
DAILY_EMAIL_MD = EMAIL_DIR / "daily_free_pick.md"


# ==============================
# Create folders if missing
# ==============================

PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
EMAIL_DIR.mkdir(parents=True, exist_ok=True)


# ==============================
# Load daily_winners tab
# ==============================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Missing Excel file: {INPUT_FILE}. "
        "Upload MLB_Prediction_Model.xlsx into mlb/data/raw/"
    )

daily_winners = pd.read_excel(INPUT_FILE, sheet_name="daily_winners")

if daily_winners.empty:
    raise ValueError("daily_winners tab is empty. No free pick can be created.")


# ==============================
# Clean and select top pick
# ==============================

daily_winners["rank"] = pd.to_numeric(daily_winners["rank"], errors="coerce")
daily_winners = daily_winners.sort_values("rank", ascending=True)

top_pick = daily_winners.iloc[0]


# ==============================
# Helper functions
# ==============================

def safe_value(row, column, default=""):
    value = row.get(column, default)

    if pd.isna(value):
        return default

    return value


def format_probability(value):
    try:
        value = float(value)

        if value <= 1:
            return round(value * 100, 1)

        return round(value, 1)
    except Exception:
        return 0


# ==============================
# Build free pick JSON
# ==============================

model_probability = format_probability(
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
    "confidence": model_probability,
    "tier": str(safe_value(top_pick, "confidence", "Pending")),
    "reason_1": str(safe_value(top_pick, "key_reason_1", "Model edge")),
    "reason_2": str(safe_value(top_pick, "key_reason_2", "Matchup advantage")),
    "reason_3": "Highest-ranked free model pick today",
    "risk": str(safe_value(top_pick, "risk_flag", "Monitor line movement and confirmed lineups.")),
    "run_line_pick": str(safe_value(top_pick, "run_line_pick", "")),
    "email_subject": f"🎯 BetLabIQ Game of the Day | {safe_value(top_pick, 'game', 'MLB')}"
}

with open(FREE_PICK_JSON, "w", encoding="utf-8") as f:
    json.dump(free_pick, f, indent=2)


# ==============================
# Build Beehiiv email draft
# ==============================

email_body = f"""# 🎯 BetLabIQ Game of the Day

## {free_pick["matchup"]}

**Game Time:** {free_pick["game_time"]}

---

## BetLabIQ Pick

# {free_pick["pick"]}

**Confidence:** {free_pick["confidence"]}/100  
**Tier:** {free_pick["tier"]}

---

## Why We Like It

✓ {free_pick["reason_1"]}

✓ {free_pick["reason_2"]}

✓ {free_pick["reason_3"]}

---

## Risk To Consider

{free_pick["risk"]}

---

## Premium Members Are Also Receiving

• Full MLB board  
• Additional premium plays  
• Props and parlay ideas  

---

No fake locks. No guarantees. Just one game we believe offers value today.

— BetLabIQ
"""

with open(DAILY_EMAIL_MD, "w", encoding="utf-8") as f:
    f.write(email_body)


print("Free pick JSON created:")
print(FREE_PICK_JSON)

print("Daily email draft created:")
print(DAILY_EMAIL_MD)
