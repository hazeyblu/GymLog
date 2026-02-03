# view/context.py

def build_user_context(user: dict):
    """
    Normalizes user data for downstream helpers
    """
    return {
        "username": user["username"],
        "name": user["name"],
        "start_weight": user.get("start_weight"),
        "active_program": user["active_program"],
        "created_at": user["created_at"],
    }
