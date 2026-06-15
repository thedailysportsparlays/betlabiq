import argparse
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def build_mlb_picks(today):
    games = [
        {
            "matchup": "Miami Marlins vs Philadelphia Phillies",
            "start_time": "6:40 PM ET",
            "home_team": "Philadelphia Phillies",
            "away_team": "Miami Marlins",
            "recommended_team": "Philadelphia Phillies",
            "confidence": 67,
            "edge": 4.5,
            "risk": "Moderate",
            "tier": "Medium",
            "reason_1": "Home-field advantage",
            "reason_2": "Stronger roster profile",
            "reason_3": "Model leans favorite side"
        },
        {
            "matchup": "Colorado Rockies vs Chicago Cubs",
            "start_time": "8:05 PM ET",
            "home_team": "Chicago Cubs",
            "away_team": "Colorado Rockies",
            "recommended_team": "Chicago Cubs",
            "confidence": 74,
            "edge": 6.2,
            "risk": "Lower",
            "tier": "High",
            "reason_1": "Home-field advantage",
            "reason_2": "Rockies road-risk profile",
            "reason_3": "Best slate model signal"
        },
        {
            "matchup": "Tampa Bay Rays vs Los Angeles Dodgers",
            "start_time": "10:10 PM ET",
            "home_team": "Los Angeles Dodgers",
            "away_team": "Tampa Bay Rays",
            "recommended_team": "Los Angeles Dodgers",
            "confidence": 70,
            "edge": 5.4,
            "risk": "Moderate",
            "tier": "High",
            "reason_1": "Elite offensive baseline",
            "reason_2": "Home-field advantage",
            "reason_3": "Model favors stronger team profile"
        }
    ]

    picks = []

    for game in games:
        picks.append({
            "date": today,
            "sport": "MLB",
            "league": "MLB",
            "matchup": game["matchup"],
            "start_time": game["start_time"],
            "market": "Moneyline",
            "pick": f'{game["recommended_team"]} ML',
            "recommended_team": game["recommended_team"],
            "odds": "TBD",
            "model_probability": game["confidence"],
            "implied_probability": round(game["confidence"] - game["edge"], 1),
            "edge": game["edge"],
            "confidence": game["confidence"],
            "tier": game["tier"],
            "risk": game["risk"],
            "is_premium": game["confidence"] >= 70,
            "reason_1": game["reason_1"],
            "reason_2": game["reason_2"],
            "reason_3": game["reason_3"]
        })

    return picks

def build_status(picks, updated_at):
    return {
        "last_updated": updated_at,
        "model_status": "Live",
        "sports_loaded": sorted(list(set(p["sport"] for p in picks))),
        "games_analyzed": len(picks),
        "free_picks": sum(1 for p in picks if not p["is_premium"]),
        "premium_picks": sum(1 for p in picks if p["is_premium"]),
        "message": "Daily board refreshed and ready."
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sport", default="all")
    parser.add_argument("--slate-date", default="today")
    args = parser.parse_args()

    today = datetime.utcnow().strftime("%Y-%m-%d")
    updated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    selected_sport = args.sport.lower()

    picks = []

    if selected_sport in ["all", "mlb"]:
        picks.extend(build_mlb_picks(today))

    status = build_status(picks, updated_at)

    with open(DATA_DIR / "todays_picks.json", "w") as f:
        json.dump(picks, f, indent=2)

    with open(DATA_DIR / "model_status.json", "w") as f:
        json.dump(status, f, indent=2)

    print(f"Updated {len(picks)} picks.")
    print("Updated model_status.json.")

if __name__ == "__main__":
    main()
