# view/workout_complete.py

import streamlit as st
from core.io import load_user_logs

def render_workout_complete():
    st.success("Good session.")

    prs = []
    if "logged_sets" in st.session_state and st.session_state.logged_sets:
        workout_id = None
        if st.session_state.workout_context:
            workout_id = st.session_state.workout_context.get("workout_id")

        # Current workout volume per exercise
        current_volume = {}
        for row in st.session_state.logged_sets:
            if row.get("is_warmup") or row.get("is_cooldown"):
                continue
            exercise = row.get("exercise")
            if not exercise:
                continue
            weight = row.get("weight") or 0.0
            reps = row.get("reps") or 0
            current_volume[exercise] = current_volume.get(exercise, 0.0) + (weight * reps)

        # Historical max volume per exercise (exclude current workout)
        if current_volume:
            user = st.session_state.user or {}
            username = user.get("username")
            if username:
                logs = load_user_logs(username)
                if not logs.empty:
                    if "is_warmup" in logs.columns:
                        logs = logs[~logs["is_warmup"]]
                    if "is_cooldown" in logs.columns:
                        logs = logs[~logs["is_cooldown"]]
                    if workout_id and "workout_id" in logs.columns:
                        logs = logs[logs["workout_id"] != workout_id]

                    if not logs.empty:
                        if "weight" not in logs.columns:
                            logs["weight"] = 0.0
                        if "reps" not in logs.columns:
                            logs["reps"] = 0
                        if "workout_id" not in logs.columns:
                            logs["workout_id"] = None

                        logs["volume"] = logs["weight"].fillna(0.0) * logs["reps"].fillna(0)
                        hist = (
                            logs.groupby(["workout_id", "exercise"], dropna=False)["volume"]
                            .sum()
                            .groupby("exercise")
                            .max()
                        )
                    else:
                        hist = None
                else:
                    hist = None

                for exercise, vol in current_volume.items():
                    if hist is None or exercise not in hist.index:
                        continue
                    if vol > float(hist.loc[exercise]):
                        prs.append((exercise, vol))

    if prs:
        st.success("Volume PRs!")
        for exercise, vol in prs:
            st.markdown(f"**{exercise}** — {vol:.0f} total volume")

    if "logged_sets" in st.session_state:
        st.subheader("Logged Sets (session)")
        st.dataframe(st.session_state.logged_sets)

    if st.button("Finish"):
        # Reset workout-related state
        st.session_state.workout_selected = False
        st.session_state.workout_context = None
        st.session_state.exercise_index = 0
        st.session_state.current_sets = []
        st.session_state.logged_sets = []
        st.rerun()
