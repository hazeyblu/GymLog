# scripts/sync_user_from_csv.py

import pandas as pd
from pathlib import Path
from datetime import datetime
import bcrypt

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent

CSV_FILE = BASE_DIR / "user.csv"
FEATHER_FILE = BASE_DIR / "users.feather"

def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def main():
    if not CSV_FILE.exists():
        raise FileNotFoundError("user.csv not found")

    csv_df = pd.read_csv(CSV_FILE)

    if len(csv_df) != 1:
        raise ValueError("user.csv must contain exactly ONE row")

    row = csv_df.iloc[0]

    # Load or initialize users.feather
    if FEATHER_FILE.exists():
        users_df = pd.read_feather(FEATHER_FILE)
    else:
        users_df = pd.DataFrame(columns=[
            "username",
            "name",
            "password_hash",
            "start_weight",
            "created_at",
            "is_active",
            "active_program"
        ])

    username = row["username"]
    exists = username in users_df["username"].values

    # ------------------------
    # OVERRIDE LOGIC
    # ------------------------
    if exists:
        print(f"⚠️ User '{username}' already exists.")
        resp = input("Override this user? (y/n): ").strip().lower()

        if resp != "y":
            print(f"❌ Aborted. User '{username}' not modified.")
            return

        # Preserve created_at
        created_at = users_df.loc[
            users_df["username"] == username, "created_at"
        ].iloc[0]

        # Remove existing user
        users_df = users_df[users_df["username"] != username]
        print(f"♻️ Updating existing user '{username}'")

    else:
        created_at = datetime.now()
        print(f"➕ Creating new user '{username}'")

    # ------------------------
    # BUILD NEW RECORD
    # ------------------------
    new_user = {
        "username": username,
        "name": row["name"],
        "password_hash": hash_password(str(row["password"])),
        "start_weight": row["start_weight"] if pd.notna(row["start_weight"]) else None,
        "created_at": created_at,
        "is_active": (
            bool(row["is_active"])
            if "is_active" in row and pd.notna(row["is_active"])
            else True
        ),
        "active_program": row["active_program"]
    }

    users_df = pd.concat(
        [users_df, pd.DataFrame([new_user])],
        ignore_index=True
    )

    users_df.to_feather(FEATHER_FILE)

    print("✔ users.feather synced successfully")

if __name__ == "__main__":
    main()
