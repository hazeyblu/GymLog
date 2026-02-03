# view/session.py

import streamlit as st

def init_session():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if "user" not in st.session_state:
        st.session_state.user = None

    if "workout_selected" not in st.session_state:
        st.session_state.workout_selected = False

    if "workout_context" not in st.session_state:
        st.session_state.workout_context = None

    # Logger-specific
    if "exercise_index" not in st.session_state:
        st.session_state.exercise_index = 0

    if "current_sets" not in st.session_state:
        st.session_state.current_sets = []

def login(user_dict: dict):
    st.session_state.authenticated = True
    st.session_state.user = user_dict

def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
