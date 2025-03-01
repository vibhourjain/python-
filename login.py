import streamlit as st
import sqlite3
import hashlib
import os
import uuid

# ========================
# CONFIGURATION (Edit these)
# ========================
DEFAULT_ADMIN_PASSWORD = "admin@123"  # Change this before deployment
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
        needs_password_reset BOOLEAN DEFAULT FALSE
    )
    """)
    
    # Create default admin user if not exists
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

def authenticate_user(username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result:
        stored_hash, salt = result
        return hash_password(password, salt) == stored_hash
    return False

# ========================
# USER MANAGEMENT
# ========================
def create_user(username, password, is_admin=False):
    cursor = conn.cursor()
    try:
        salt = generate_salt()
        password_hash = hash_password(password, salt)
        cursor.execute("""
            INSERT INTO users (username, password_hash, salt, is_admin)
            VALUES (?, ?, ?, ?)
        """, (username, password_hash, salt, is_admin))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def update_password(username, new_password):
    cursor = conn.cursor()
    salt = generate_salt()
    new_hash = hash_password(new_password, salt)
    cursor.execute("""
        UPDATE users 
        SET password_hash = ?, salt = ?, needs_password_reset = ?
        WHERE username = ?
    """, (new_hash, salt, False, username))
    conn.commit()

# ========================
# STREAMLIT APP
# ========================
def main():
    st.set_page_config(page_title="Secure Auth System", layout="wide")
    
    # Session state initialization
    if 'auth' not in st.session_state:
        st.session_state.auth = {
            'logged_in': False,
            'username': None,
            'is_admin': False,
            'session_token': None
        }

    # Login/Registration Interface
    if not st.session_state.auth['logged_in']:
        st.title("Secure Authentication System")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Login/Register"):
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
                user_exists = cursor.fetchone()
                
                if user_exists:
                    if authenticate_user(username, password):
                        st.session_state.auth = {
                            'logged_in': True,
                            'username': username,
                            'is_admin': is_admin_user(username),
                            'session_token': str(uuid.uuid4())
                        }
                        st.experimental_rerun()
                    else:
                        st.error("Incorrect password")
                else:
                    # New user registration
                    if len(password) < 8:
                        st.error("Password must be at least 8 characters")
                    else:
                        if create_user(username, password):
                            st.success("Account created successfully! Please login")
                        else:
                            st.error("Username already exists")

        with col2:
            if st.button("Admin Password Reset"):
                # Verify admin credentials before allowing password reset
                admin_username = st.text_input("Admin Username")
                admin_password = st.text_input("Admin Password", type="password")
                target_user = st.text_input("User to reset")
                new_password = st.text_input("New Password", type="password")
                
                if st.button("Reset Password"):
                    if authenticate_user(admin_username, admin_password) and is_admin_user(admin_username):
                        update_password(target_user, new_password)
                        st.success("Password reset successfully")
                    else:
                        st.error("Invalid admin credentials")

    # Authenticated Interface
    else:
        st.sidebar.title(f"Welcome {st.session_state.auth['username']}")
        if st.sidebar.button("Logout"):
            st.session_state.auth['logged_in'] = False
            st.experimental_rerun()
        
        # Password Change Section
        with st.expander("Change Password"):
            old_password = st.text_input("Old Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.button("Update Password"):
                if not authenticate_user(st.session_state.auth['username'], old_password):
                    st.error("Incorrect current password")
                elif new_password != confirm_password:
                    st.error("New passwords don't match")
                else:
                    update_password(st.session_state.auth['username'], new_password)
                    st.success("Password updated successfully")

        # Admin Panel
        if st.session_state.auth['is_admin']:
            with st.sidebar.expander("Admin Panel"):
                reset_user = st.text_input("User to reset")
                new_admin_password = st.text_input("New Password", type="password")
                if st.button("Force Password Reset"):
                    update_password(reset_user, new_admin_password)
                    st.success("Password reset completed")

        # Main Application Content
        st.title("Secure Application Dashboard")
        st.write("Your protected content goes here")

def is_admin_user(username):
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    return result[0] if result else False

if __name__ == "__main__":
    main()
