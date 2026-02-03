# scripts/delete_users.py

import argparse
from pathlib import Path
import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
USERS_FEATHER = BASE_DIR / "users.feather"
LOGS_DIR = BASE_DIR / "logs"

BODY_METRICS_SUFFIX = "_body.feather"

def parse_args():
    parser = argparse.ArgumentParser(
        description="Delete users and their associated logs."
    )
    parser.add_argument(
        "--username",
        action="append",
        dest="usernames",
        help="Username to delete (can be repeated)."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Delete all users."
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt."
    )
    return parser.parse_args()

def confirm_or_exit(prompt: str, force: bool):
    if force:
        return
    resp = input(f"{prompt} (y/n): ").strip().lower()
    if resp != "y":
        print("❌ Aborted.")
        raise SystemExit(1)

def delete_logs_for_user(username: str):
    if not LOGS_DIR.exists():
        return

    workout_log = LOGS_DIR / f"{username}.feather"
    body_log = LOGS_DIR / f"{username}{BODY_METRICS_SUFFIX}"

    if workout_log.exists():
        workout_log.unlink()
    if body_log.exists():
        body_log.unlink()

def main():
    args = parse_args()

    if not USERS_FEATHER.exists():
        raise FileNotFoundError("users.feather not found")

    if not args.all and not args.usernames:
        raise ValueError("Provide --username (repeatable) or --all")

    users_df = pd.read_feather(USERS_FEATHER)
    columns = list(users_df.columns)

    if args.all:
        confirm_or_exit("⚠️ Delete ALL users and logs?", args.yes)
        usernames = users_df["username"].tolist()
        users_df = pd.DataFrame(columns=columns)
    else:
        usernames = [u for u in args.usernames if u]
        missing = [u for u in usernames if u not in users_df["username"].values]
        if missing:
            print(f"⚠️ User(s) not found: {', '.join(missing)}")

        confirm_or_exit(
            f"⚠️ Delete {len(usernames)} user(s) and logs?",
            args.yes
        )
        users_df = users_df[~users_df["username"].isin(usernames)]

    users_df.to_feather(USERS_FEATHER)

    for username in usernames:
        delete_logs_for_user(username)

    print("✅ Delete complete.")

if __name__ == "__main__":
    main()
