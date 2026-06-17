import json
from datetime import datetime, timedelta
from pathlib import Path

import requests


BASE_DIR = Path(__file__).resolve().parents[1]

ARCHIVE_DIR = BASE_DIR / "data" / "picks" / "free_pick_archive"
PUBLIC_DIR = BASE_DIR / "data" / "public"

PICK_HISTORY_JSON = PUBLIC_DIR / "pick_history.json"
RESULTS_SUMMARY_JSON = PUBLIC_DIR / "results_summary.json"

PUBLIC_DIR.mkdir(parents=True, exist_ok=True)


def load_json(path, default):
    if not path.exists():
        return default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_yesterday_date():
    return (datetime.now() - timedelta(days=1)).date()


def get_game_result_by_game_pk(game_pk):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    game_data = data.get("gameData", {})
    live_data = data.get("liveData", {})

    status = game_data.get("status", {})
    teams = game_data.get("teams", {})
    linescore = live_data.get("linescore", {})

    away_team = teams.get("away", {}).get("name", "")
    home_team = teams.get("home", {}).get("name", "")

    away_score = linescore.get("teams", {}).get("away", {}).get("runs")
    home_score = linescore.get("teams", {}).get("home", {}).get("runs")

    abstract_state = status.get("abstractGameState", "")
    detailed_state = status.get("detailedState", "")

    return {
        "away_team": away_team,
        "home_team": home_team,
        "away_score": away_score,
        "home_score": home_score,
        "abstract_state": abstract_state,
        "detailed_state": detailed_state
    }


def clean_team_name(value):
    return (
        str(value)
        .lower()
        .replace(" moneyline", "")
        .replace(" ml", "")
        .replace(".", "")
        .strip()
    )


def determine_pick_result(pick, game_result):
    if game_result["abstract_state"] != "Final":
        return {
            "result": "Pending",
            "units": 0.0,
            "notes": f"Game not final yet: {game_result['detailed_state']}"
        }

    away_team = clean_team_name(game_result["away_team"])
    home_team = clean_team_name(game_result["home_team"])
    picked_team = clean_team_name(pick.get("pick", ""))

    away_score = game_result["away_score"]
    home_score = game_result["home_score"]

    if away_score is None or home_score is None:
        return {
            "result": "Pending",
            "units": 0.0,
            "notes": "Final score not available yet."
        }

    if picked_team == away_team:
        picked_score = away_score
        opponent_score = home_score
    elif picked_team == home_team:
        picked_score = home_score
        opponent_score = away_score
    else:
        return {
            "result": "Pending",
            "units": 0.0,
            "notes": "Picked team did not match MLB home or away team name."
        }

    final_score_note = (
        f"Final score: {game_result['away_team']} {away_score}, "
        f"{game_result['home_team']} {home_score}"
    )

    if picked_score > opponent_score:
        return {
            "result": "Win",
            "units": 1.0,
            "notes": final_score_note
        }

    if picked_score < opponent_score:
        return {
            "result": "Loss",
            "units": -1.0,
            "notes": final_score_note
        }

    return {
        "result": "Push",
        "units": 0.0,
        "notes": final_score_note
    }


def upsert_history(history, record):
    existing_ids = [item.get("pick_id") for item in history]

    if record["pick_id"] in existing_ids:
        return [
            record if item.get("pick_id") == record["pick_id"] else item
            for item in history
        ]

    history.append(record)
    return history


def build_summary(history):
    wins = sum(1 for x in history if x.get("result") == "Win")
    losses = sum(1 for x in history if x.get("result") == "Loss")
    pushes = sum(1 for x in history if x.get("result") == "Push")
    pending = sum(1 for x in history if x.get("result") == "Pending")

    decisions = wins + losses
    win_rate = round((wins / decisions) * 100, 1) if decisions else 0.0
    units = round(sum(float(x.get("units", 0)) for x in history), 1)

    latest = history[-1] if history else {
        "date": "",
        "matchup": "",
        "pick": "",
        "result": "Pending"
    }

    return {
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "pending": pending,
        "record": f"{wins}-{losses}",
        "win_rate": f"{win_rate}%",
        "units": f"{units:+.1f}",
        "last_pick": {
            "date": latest.get("date", ""),
            "matchup": latest.get("matchup", ""),
            "pick": latest.get("pick", ""),
            "result": latest.get("result", "Pending")
        },
        "updated_at": datetime.now().isoformat()
    }


def main():
    target_date = get_yesterday_date()
    archive_file = ARCHIVE_DIR / f"{target_date}.json"

    print(f"Checking archived pick for: {target_date}")
    print(f"Archive file: {archive_file}")

    if not archive_file.exists():
        raise FileNotFoundError(
            f"No archived pick found for {target_date}. "
            "Make sure yesterday's free pick was archived."
        )

    pick = load_json(archive_file, {})
    game_pk = pick.get("game_pk", "")

    if not game_pk:
        raise ValueError("Archived pick is missing game_pk.")

    game_result = get_game_result_by_game_pk(game_pk)
    result_info = determine_pick_result(pick, game_result)

    record = {
        "pick_id": pick.get("pick_id"),
        "date": pick.get("date"),
        "sport": "MLB",
        "game_pk": pick.get("game_pk"),
        "matchup": pick.get("matchup"),
        "pick": pick.get("pick"),
        "confidence": pick.get("confidence"),
        "tier": pick.get("tier"),
        "result": result_info["result"],
        "units": result_info["units"],
        "notes": result_info["notes"],
        "checked_at": datetime.now().isoformat()
    }

    history = load_json(PICK_HISTORY_JSON, [])
    history = upsert_history(history, record)
    history = sorted(history, key=lambda x: x.get("date", ""))

    summary = build_summary(history)

    save_json(PICK_HISTORY_JSON, history)
    save_json(RESULTS_SUMMARY_JSON, summary)

    print("Updated:", PICK_HISTORY_JSON)
    print("Updated:", RESULTS_SUMMARY_JSON)
    print("Result:", record["result"])
    print("Record:", summary["record"])
    print("Win rate:", summary["win_rate"])
    print("Units:", summary["units"])


if __name__ == "__main__":
    main()
