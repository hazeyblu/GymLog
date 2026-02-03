# view/workout_selector.py

import streamlit as st
from datetime import date, datetime
import uuid
from core.io import append_body_metrics, load_body_metrics
from core.programs import load_program_meta
from view.session import init_session

def render_workout_selector(user_ctx: dict):
    """
    Allows user to select which workout to run today.
    Populates st.session_state.workout_context
    """

    init_session()

    program_name = user_ctx["active_program"]
    meta = load_program_meta(program_name)

    # ---- Auto-detect day ----
    today = date.today()
    today_name = today.strftime("%A")

    days = meta["days"]  # list of {day_id, day_name}
    day_name_to_id = {d["day_name"]: d["day_id"] for d in days}

    detected_day_id = day_name_to_id.get(today_name)

    st.header("Select Workout")
    st.caption(f"Program: {program_name}")

    # ---- Day selection ----
    day_options = [
        f"{d['day_id']} — {d['day_name']}"
        for d in days
    ]

    default_index = (
        list(day_name_to_id.values()).index(detected_day_id)
        if detected_day_id in day_name_to_id.values()
        else 0
    )

    selected = st.selectbox(
        "Workout day",
        options=day_options,
        index=default_index
    )

    selected_day_id = int(selected.split("—")[0].strip())
    selected_day_name = next(
        d["day_name"] for d in days if d["day_id"] == selected_day_id
    )

    # ---- Workout name (display only) ----
    workout_names = [
        w["workout_name"]
        for w in meta["workouts"]
        if w["day_id"] == selected_day_id
    ]

    workout_name = workout_names[0] if workout_names else "Workout"

    st.markdown(f"**Workout:** {workout_name}")
    st.markdown(f"**Date:** {today.isoformat()}")

    # ---- Weight logging (optional) ----
    with st.expander("Log body weight (optional)"):
        weight_value = st.number_input("Weight (kg)", min_value=0.0, step=0.1, key="weight_value")
        if st.button("Save weight"):
            user = st.session_state.user or {}
            username = user.get("username")
            if username and weight_value > 0:
                append_body_metrics(
                    username,
                    [
                        {
                            "logged_at": datetime.now().isoformat(timespec="seconds"),
                            "weight": float(weight_value),
                            "unit": "kg",
                        }
                    ],
                )
                st.success("Weight saved")

        user = st.session_state.user or {}
        username = user.get("username")
        if username:
            metrics = load_body_metrics(username)
            if not metrics.empty and "weight" in metrics.columns:
                weight_rows = metrics.dropna(subset=["weight"])
                if len(weight_rows) >= 3:
                    chart_df = weight_rows[["logged_at", "weight"]].copy()
                    chart_df = chart_df.sort_values("logged_at")
                    st.line_chart(chart_df, x="logged_at", y="weight")

    # ---- Start button ----
    if st.button("▶ Start Workout"):
        st.session_state.workout_context = {
            "program_name": program_name,
            "day_id": selected_day_id,
            "day_name": selected_day_name,
            "workout_name": workout_name,
            "date": today,
            "workout_id": uuid.uuid4().hex,
        }
        st.session_state.workout_selected = True
        st.success("Workout locked in")
        st.rerun()
