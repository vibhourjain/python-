import streamlit as st
import sqlite3
import hashlib
import os
import uuid

# ========================
# CONFIGURATION
# ========================
DEFAULT_ADMIN_PASSWORD = "admin@123"  # Change before deployment
DATABASE_NAME = "user_auth.db"

# ========================
# DATABASE SETUP
# ========================
def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT,
        salt TEXT,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create default admin if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        salt = os.urandom(16).hex()
        password_hash = hashlib.sha256((DEFAULT_ADMIN_PASSWORD + salt).encode()).hexdigest()
        cursor.execute("""
            INSERT INTO users (username, password_hash, salt, is_admin)
            VALUES (?, ?, ?, ?)
        """, ("admin", password_hash, salt, True))
    
    conn.commit()
    return conn

conn = init_db()

# ========================
# SECURITY FUNCTIONS
# ========================
def generate_salt():
    return os.urandom(16).hex()

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def authenticate(username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        stored_hash, salt = result
        return hash_password(password, salt) == stored_hash
    return False

# ========================
# STREAMLIT APP
# ========================
def login_page():
    # Add this custom CSS block
    st.markdown("""
    <style>
    /* Main page background */
    .stApp {
        background-color: #2E3440;
    }
    
    /* Login container */
    .stForm {
        background-color: #3B4252 !important;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Input fields */
    .stTextInput input, .stTextInput label, 
    .stPassword input, .stPassword label {
        color: #ECEFF4 !important;
        background-color: #434C5E !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #88C0D0 !important;
        color: #2E3440 !important;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Headers */
    h1 {
        color: #88C0D0 !important;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Success/error messages */
    .stAlert {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    st.title("ISHIN- Authentication")
    
    with st.form("auth_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login/Register")

        if submitted:
            if not username or not password:
                st.error("Please fill all fields")
                return

            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            
            if cursor.fetchone():  # Existing user
                if authenticate(username, password):
                    st.session_state.auth = {
                        'logged_in': True,
                        'username': username,
                        'is_admin': is_admin(username),
                        'session_id': str(uuid.uuid4())
                    }
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            else:  # New user
                if len(password) < 8:
                    st.error("Password must be ≥8 characters")
                else:
                    salt = generate_salt()
                    password_hash = hash_password(password, salt)
                    try:
                        cursor.execute("""
                            INSERT INTO users (username, password_hash, salt)
                            VALUES (?, ?, ?)
                        """, (username, password_hash, salt))
                        conn.commit()
                        st.success("Account created! Please login")
                    except sqlite3.IntegrityError:
                        st.error("Username already exists")

def dashboard():
    st.sidebar.title(f"Welcome {st.session_state.auth['username']}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
    
    # Password change section
    with st.expander("🔒 Password Management"):
        with st.form("change_pass"):
            old_pass = st.text_input("Current Password", type="password")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Update Password"):
                if not authenticate(st.session_state.auth['username'], old_pass):
                    st.error("Current password incorrect")
                elif new_pass != confirm_pass:
                    st.error("Passwords don't match")
                else:
                    update_password(st.session_state.auth['username'], new_pass)
                    st.success("Password updated successfully")

    # Admin panel
    if st.session_state.auth['is_admin']:
        with st.sidebar.expander("🛡️ Admin Tools"):
            with st.form("admin_reset"):
                target_user = st.text_input("Username to reset")
                new_pass = st.text_input("New Password", type="password")
                if st.form_submit_button("Force Password Reset"):
                    update_password(target_user, new_pass)
                    st.success("Password reset complete")

    # Main content
    st.title("Secure Dashboard")
    st.write("Your protected content here")

def update_password(username, new_password):
    cursor = conn.cursor()
    salt = generate_salt()
    new_hash = hash_password(new_password, salt)
    cursor.execute("""
        UPDATE users 
        SET password_hash = ?, salt = ?
        WHERE username = ?
    """, (new_hash, salt, username))
    conn.commit()

def is_admin(username):
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result[0] if result else False

def main():
    st.set_page_config(page_title="Secure System", layout="wide")
    
    if 'auth' not in st.session_state:
        st.session_state.auth = {'logged_in': False}

    if st.session_state.auth['logged_in']:
        dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()
