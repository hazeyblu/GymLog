# app.py

import streamlit as st

from view.session import init_session, logout
from core.io import delete_workout_by_id
from view.auth import render_login
from view.context import build_user_context
from view.workout_selector import render_workout_selector
from view.logger import render_logger
from view.workout_complete import render_workout_complete

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="GymLog",
    layout="centered"
)

# ---- Global UI tweaks ----
st.markdown(
    """
    <style>
    /* Center the button element within its container */
    div.stButton {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# SESSION INIT
# -------------------------
init_session()

if "workout_completed" not in st.session_state:
    st.session_state.workout_completed = False

# -------------------------
# AUTH GATE
# -------------------------
if not st.session_state.authenticated:
    render_login()
    st.stop()

# -------------------------
# USER CONTEXT
# -------------------------
user_ctx = build_user_context(st.session_state.user)

# -------------------------
# SIDEBAR
# -------------------------
with st.sidebar:
    st.markdown(f"### 👤 {user_ctx['name']}")
    st.markdown(f"**Program:** {user_ctx['active_program']}")

    if st.session_state.workout_selected and not st.session_state.workout_completed:
        if "cancel_confirm" not in st.session_state:
            st.session_state.cancel_confirm = False

        if st.button("Cancel session"):
            st.session_state.cancel_confirm = True
            st.rerun()

        if st.session_state.cancel_confirm:
            st.warning("Canceling will erase this workout's progress.")
            if st.button("Confirm cancel"):
                wc = st.session_state.workout_context or {}
                workout_id = wc.get("workout_id")
                username = (st.session_state.user or {}).get("username")
                if username and workout_id:
                    delete_workout_by_id(username, workout_id)

                st.session_state.workout_selected = False
                st.session_state.workout_completed = False
                st.session_state.workout_context = None
                st.session_state.exercise_index = 0
                st.session_state.current_sets = []
                st.session_state.logged_sets = []
                st.session_state.cancel_confirm = False
                st.rerun()

            if st.button("Keep workout"):
                st.session_state.cancel_confirm = False
                st.rerun()

    if st.button("Logout"):
        logout()
        st.rerun()

# -------------------------
# MAIN ROUTER
# -------------------------

# 1️⃣ No workout selected yet → selector
if not st.session_state.workout_selected:
    render_workout_selector(user_ctx)

# 2️⃣ Workout selected but not completed → logger
elif not st.session_state.workout_completed:
    render_logger(user_ctx)

# 3️⃣ Workout completed → summary / finish
else:
    render_workout_complete()
