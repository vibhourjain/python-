import streamlit as st
import sqlite3
import hashlib
import os
import uuid
import main_sre_auto_app  # Import your main app

# ========================
# CONFIGURATION
# ========================
DEFAULT_ADMIN_PASSWORD = "admin@123"  # Move this to an environment variable in production
DATABASE_NAME = "user_auth.db"

# ========================
# DATABASE FUNCTIONS
# ========================
def get_db_connection():
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    conn = get_db_connection()
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
    
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        salt = os.urandom(16).hex()
        password_hash = hashlib.sha256((DEFAULT_ADMIN_PASSWORD + salt).encode()).hexdigest()
        cursor.execute("""
            INSERT INTO users (username, password_hash, salt, is_admin)
            VALUES (?, ?, ?, ?)
        """, ("admin", password_hash, salt, True))
    
    conn.commit()
    conn.close()

init_db()

# ========================
# SECURITY FUNCTIONS
# ========================
def generate_salt():
    return os.urandom(16).hex()

def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()

def authenticate(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, salt FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        stored_hash, salt = result
        return hash_password(password, salt) == stored_hash
    return False

def is_admin(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else False

def update_password(username, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()
    salt = generate_salt()
    new_hash = hash_password(new_password, salt)
    cursor.execute("""
        UPDATE users 
        SET password_hash = ?, salt = ?
        WHERE username = ?
    """, (new_hash, salt, username))
    conn.commit()
    conn.close()

def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, is_admin FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def delete_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# ========================
# STREAMLIT UI
# ========================
def login_page():
    st.title("ISHIN - Authentication")
    with st.form("auth_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login/Register")
        
        if submitted:
            if not username or not password:
                st.error("Please fill all fields")
                return
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            user_exists = cursor.fetchone()
            conn.close()
            
            if user_exists:  # Existing user
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
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)", (username, password_hash, salt))
                        conn.commit()
                        st.success("Account created! Please login")
                    except sqlite3.IntegrityError:
                        st.error("Username already exists")
                    conn.close()

def admin_panel():
    st.title("Admin Panel")
    users = get_all_users()
    st.write("### Manage Users")
    for user in users:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(user[0])
        if col2.button("Reset Password", key=f"reset_{user[0]}"):
            update_password(user[0], "NewPass@123")
            st.success(f"Password reset for {user[0]}")
        if not user[1] and col3.button("Delete", key=f"del_{user[0]}"):
            delete_user(user[0])
            st.success(f"User {user[0]} deleted")
            st.rerun()

def main():
    if 'auth' not in st.session_state:
        st.session_state.auth = {'logged_in': False}

    if st.session_state.auth['logged_in']:
        if st.session_state.auth['is_admin']:
            admin_panel()
        else:
            main_sre_auto_app.run()  # Run the main application after successful login
    else:
        login_page()

if __name__ == "__main__":
    main()
