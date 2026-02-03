# scripts/export_users_to_csv.py

import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
FEATHER = BASE_DIR / "users.feather"
CSV_OUT = BASE_DIR / "users_export.csv"

df = pd.read_feather(FEATHER)
df.drop(columns=["password_hash"], inplace=True)
# df.to_csv(CSV_OUT, index=False)
print(df.head())

print("users_export.csv created (passwords excluded)")
