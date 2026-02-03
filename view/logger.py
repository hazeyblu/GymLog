# view/logger.py

import streamlit as st
from core.programs import load_day
from core.io import append_workout_logs, now_iso, load_user_logs

def render_logger(user_ctx: dict):
    """
    Exercise-by-exercise workout logger
    """

    wc = st.session_state.workout_context
    program_name = wc["program_name"]
    day_id = wc["day_id"]

    workout_df = load_day(program_name, day_id).reset_index(drop=True)

    idx = st.session_state.exercise_index

    # ---- End of workout ----
    if idx >= len(workout_df):
        st.session_state.workout_completed = True
        st.rerun()

    row = workout_df.iloc[idx]

    exercise = row["exercise"]
    target_sets = row["target_sets"]
    rep_min = row["rep_min"]
    rep_max = row["rep_max"]
    weight_required = row["weight_required"]
    is_warmup = row["is_warmup"]
    is_cooldown = row["is_cooldown"]

    # ---- Header ----
    st.header(exercise)
    st.caption(f"{target_sets} × {rep_min}–{rep_max}")

    if is_warmup:
        st.info("Warm-up")
    elif is_cooldown:
        st.info("Cool-down")

    # ---- Initialize first set (with prefill) ----
    if not st.session_state.current_sets:
        prefill_sets = []
        logs = load_user_logs(user_ctx["username"])
        if not logs.empty:
            if "exercise" in logs.columns:
                logs = logs[logs["exercise"] == exercise]
            if "is_warmup" in logs.columns:
                logs = logs[~logs["is_warmup"]]
            if "is_cooldown" in logs.columns:
                logs = logs[~logs["is_cooldown"]]

            if not logs.empty:
                if "logged_at" in logs.columns:
                    logs = logs.sort_values("logged_at")
                    last_logged_at = logs["logged_at"].iloc[-1]
                    logs = logs[logs["logged_at"] == last_logged_at]

                if "set_number" in logs.columns:
                    logs = logs.sort_values("set_number")

                for _, r in logs.iterrows():
                    weight_value = None
                    if weight_required:
                        try:
                            weight_value = float(r["weight"])
                        except Exception:
                            weight_value = 0.0

                    try:
                        reps_value = int(r["reps"])
                    except Exception:
                        reps_value = 0

                    prefill_sets.append(
                        {
                            "weight": weight_value,
                            "reps": reps_value
                        }
                    )

        if prefill_sets:
            st.session_state.current_sets.extend(prefill_sets)
        else:
            st.session_state.current_sets.append(
                {"weight": 0.0 if weight_required else None, "reps": 0}
            )

    # ---- Render sets ----
    for i, s in enumerate(st.session_state.current_sets):
        cols = st.columns(2)
        with cols[0]:
            if weight_required:
                s["weight"] = st.number_input(
                    f"Set {i+1} Weight",
                    value=float(s["weight"]),
                    step=2.5,
                    key=f"w_{idx}_{i}"
                )
        with cols[1]:
            s["reps"] = st.number_input(
                f"Set {i+1} Reps",
                value=int(s["reps"]),
                step=1,
                key=f"r_{idx}_{i}"
            )

    # ---- Action buttons ----
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("➕"):
            last = st.session_state.current_sets[-1]
            st.session_state.current_sets.append(
                {
                    "weight": last["weight"],
                    "reps": last["reps"]
                }
            )
            st.rerun()

    with c2:
        if st.button("✔ Save & Next"):
            # Persist + store in session
            if "logged_sets" not in st.session_state:
                st.session_state.logged_sets = []

            date_value = wc["date"]
            date_iso = date_value.isoformat() if hasattr(date_value, "isoformat") else str(date_value)
            logged_at = now_iso()
            workout_id = wc.get("workout_id")

            rows = []
            for i, s in enumerate(st.session_state.current_sets):
                row = {
                    "username": user_ctx["username"],
                    "date": date_iso,
                    "logged_at": logged_at,
                    "program": program_name,
                    "day_id": day_id,
                    "day_name": wc.get("day_name"),
                    "workout_name": wc.get("workout_name"),
                    "workout_id": workout_id,
                    "exercise": exercise,
                    "set_number": i + 1,
                    "weight": s["weight"],
                    "reps": s["reps"],
                    "is_warmup": is_warmup,
                    "is_cooldown": is_cooldown
                }
                rows.append(row)
                st.session_state.logged_sets.append(row)

            append_workout_logs(user_ctx["username"], rows)

            st.session_state.current_sets = []
            st.session_state.exercise_index += 1
            st.rerun()

    with c3:
        if st.button("⏭️"):
            st.session_state.current_sets = []
            st.session_state.exercise_index += 1
            st.rerun()
