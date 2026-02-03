# core/users.py

import pandas as pd
import bcrypt
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
USERS_FEATHER = PROJECT_ROOT / "users.feather"

def load_users():
    if not USERS_FEATHER.exists():
        raise FileNotFoundError("users.feather not found")
    return pd.read_feather(USERS_FEATHER)

def verify_user(username: str, password: str):
    """
    Returns user row (dict) if valid, else None
    """
    users = load_users()
    user = users[users["username"] == username]

    if user.empty:
        return None

    user = user.iloc[0]

    if not user["is_active"]:
        return None

    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return user.to_dict()

    return None

def reset_password(username: str, name: str, new_password: str) -> bool:
    users = load_users()
    user_idx = users.index[users["username"] == username]
    if len(user_idx) == 0:
        return False

    i = user_idx[0]
    if str(users.at[i, "name"]) != str(name):
        return False

    users.at[i, "password_hash"] = bcrypt.hashpw(
        new_password.encode(), bcrypt.gensalt()
    ).decode()

    users.to_feather(USERS_FEATHER)
    return True
