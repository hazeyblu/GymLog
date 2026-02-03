# GymLog

GymLog is a mobile-first Streamlit app for logging gym workouts with a linear, one-exercise-per-screen flow.

## Project Structure
- `app.py` — Streamlit entrypoint (routing only)
- `core/` — business logic (no Streamlit imports)
- `view/` — Streamlit UI + session orchestration
- `programs/` — compiled workout programs (`meta.json`, `day_*.feather`)
- `users.feather` — user auth source
- `logs/` — per-user workout logs (append-only) + body metrics (`*_body.feather`)
- `scripts/` — admin utilities
- `workouts.csv` — human-edited workout definition (optional in repo)

## Running Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run Streamlit:
   ```bash
   streamlit run app.py
   ```
