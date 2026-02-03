# scripts/compile_workouts_from_csv.py

import pandas as pd
from pathlib import Path
import json

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent

CSV_FILE = BASE_DIR / "workouts.csv"
PROGRAMS_DIR = BASE_DIR / "programs"

def main():
    df = pd.read_csv(CSV_FILE)

    required_cols = {
        "split_type", "day_id", "day_name", "order", "exercise",
        "workout_name", "target_sets", "rep_min", "rep_max",
        "weight_required", "is_warmup", "is_cooldown"
    }

    if not required_cols.issubset(df.columns):
        raise ValueError("workouts.csv missing required columns")

    for split_type, split_df in df.groupby("split_type"):
        print(f"\n📦 Compiling split: {split_type}")

        split_dir = PROGRAMS_DIR / split_type
        split_dir.mkdir(parents=True, exist_ok=True)

        # ---- META ----
        meta = {
            "program_name": split_type,
            "days": (
                split_df[["day_id", "day_name"]]
                .drop_duplicates()
                .sort_values("day_id")
                .to_dict(orient="records")
            ),
            "workouts": (
                split_df[["day_id", "workout_name"]]
                .drop_duplicates()
                .to_dict(orient="records")
            )
        }

        with open(split_dir / "meta.json", "w") as f:
            json.dump(meta, f, indent=2)

        # ---- DAY FILES ----
        for day_id, day_df in split_df.groupby("day_id"):
            out = day_df.sort_values("order")[
                [
                    "order", "exercise", "workout_name",
                    "target_sets", "rep_min", "rep_max",
                    "weight_required", "is_warmup", "is_cooldown"
                ]
            ]

            out.to_feather(split_dir / f"day_{int(day_id)}.feather")
            print(f"  ✅ day_{day_id}.feather written")

    print("\n✔ Workout compilation complete")

if __name__ == "__main__":
    main()
