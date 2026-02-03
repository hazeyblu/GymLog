# view/auth.py

import streamlit as st
from core.users import verify_user, reset_password
from view.session import login

def render_login():
    st.title("GymLog")

    if "show_reset" not in st.session_state:
        st.session_state.show_reset = False

    if not st.session_state.show_reset:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = verify_user(username, password)

            if user:
                login(user)
                st.success("Logged in")
                st.rerun()
            else:
                st.error("Invalid credentials or inactive user")

        if st.button("Forgot password?"):
            st.session_state.show_reset = True
            st.rerun()
    else:
        st.subheader("Reset password")

        username = st.text_input("Username", key="reset_username")
        name = st.text_input("Name", key="reset_name")
        new_password = st.text_input("New password", type="password", key="reset_new_pw")
        confirm_password = st.text_input("Confirm new password", type="password", key="reset_confirm_pw")

        if st.button("Set new password"):
            if not username or not name or not new_password:
                st.error("All fields are required")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                ok = reset_password(username, name, new_password)
                if ok:
                    st.success("Password updated. You can log in now.")
                    st.session_state.show_reset = False
                    st.rerun()
                else:
                    st.error("Username and name did not match")

        if st.button("Back to login"):
            st.session_state.show_reset = False
            st.rerun()
