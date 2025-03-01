import streamlit as st
import sqlite3
import hashlib
import os
import uuid  # For generating session tokens

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('user_data.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT,
        salt TEXT
    )
    """)
    conn.commit()
    return conn

# Function to generate a salt
def generate_salt():
    return os.urandom(16).hex()

# Function to hash passwords with a salt
def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

# Function to create a new user
def create_user(username, password):
    salt = generate_salt()
    password_hash = hash_password(password, salt)
    cursor.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, password_hash, salt))
    conn.commit()

# Function to authenticate user
def authenticate_user(username, password):
    cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        stored_hash, salt = result
        return hash_password(password, salt) == stored_hash
    return False

# Initialize database and cursor
conn = init_db()
cursor = conn.cursor()

# Streamlit App
def main():
    # Set page config for theme and title
    st.set_page_config(
        page_title="Login App",
        page_icon="🔒",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # Custom theme (optional)
    st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Check if user is logged in
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None

    # Login Page
    if not st.session_state.logged_in:
        st.title("🔒 Login Page")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            if authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.session_token = str(uuid.uuid4())  # Generate a unique session token
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password.")

    # If logged in, show app functionalities
    if st.session_state.logged_in:
        st.sidebar.title(f"Welcome, {st.session_state.username}!")
        st.sidebar.write("You are logged in.")

        # Display the username (for demonstration purposes)
        st.write(f"Logged in as: **{st.session_state.username}**")

        # Example functionality 1: Display user-specific data
        st.subheader("User-Specific Data")
        st.write(f"Here is some data for {st.session_state.username}.")

        # Example functionality 2: Perform an action using the username
        st.subheader("Perform an Action")
        if st.button("Say Hello"):
            st.write(f"Hello, {st.session_state.username}!")

        # Logout button
        logout_button = st.sidebar.button("Logout")
        if logout_button:
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.session_token = None
            st.experimental_rerun()

if __name__ == "__main__":
    main()
