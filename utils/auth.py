import streamlit as st
import hmac

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        try:
            # Try to get password from secrets, fail gracefully if file/key missing
            stored_password = st.secrets.get("password", "admin123")
        except Exception: 
            # Fallback if secrets.toml file doesn't exist
            stored_password = "admin123"

        if hmac.compare_digest(st.session_state["password"], stored_password):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # Return True if key already validated
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password
    st.markdown(
        """
        <style>
        .stTextInput {max-width: 400px; margin: 0 auto;}
        .app-header {text-align: center; margin-bottom: 30px;}
        </style>
        """, unsafe_allow_html=True
    )
    
    st.markdown("<h1 class='app-header'>🔒 Login Required</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        if "password_correct" in st.session_state:
            st.error("😕 Password incorrect")
            
    return False
