# scripts/export_program_to_csv.py

import pandas as pd
from pathlib import Path
import json

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
PROGRAM_DIR = BASE_DIR / "programs" / "PPL_v1"
CSV_OUT = BASE_DIR / "workouts_export.csv"

rows = []

with open(PROGRAM_DIR / "meta.json") as f:
    meta = json.load(f)

for day in meta["days"]:
    day_id = day["day_id"]
    day_name = day["day_name"]

    df = pd.read_feather(PROGRAM_DIR / f"day_{day_id}.feather")
    df["day_id"] = day_id
    df["day_name"] = day_name
    df["split_type"] = meta["program_name"]

    rows.append(df)

out = pd.concat(rows, ignore_index=True)
out.to_csv(CSV_OUT, index=False)

print("workouts_export.csv created")
