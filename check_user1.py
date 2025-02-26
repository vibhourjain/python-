import streamlit as st
import pyodbc

# Define the mapping of applications to Sybase instances and SQL queries
app_mapping = {
    "App1": {
        "instance": "SybaseInstance1",
        "sql_query": "SELECT * FROM users WHERE username = ?"
    },
    "App2": {
        "instance": "SybaseInstance2",
        "sql_query": "SELECT * FROM users WHERE username = ?"
    },
    # Add mappings for App3, App4, and App5
}

# Function to check user access
def check_user_access(instance, sql_query, username):
    try:
        # Connect to the Sybase instance (replace with your connection details)
        conn = pyodbc.connect(
            f"DRIVER={{Sybase}};SERVER={instance};DATABASE=your_db;UID=your_user;PWD=your_password"
        )
        cursor = conn.cursor()
        
        # Execute the SQL query with the provided username
        cursor.execute(sql_query, (username,))
        result = cursor.fetchone()
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Return True if the user exists, otherwise False
        return result is not None
    except Exception as e:
        st.error(f"Error checking user access: {e}")
        return False

# Streamlit app
st.title("User Access Check")

# User selects the application
selected_app = st.selectbox("Select Application", list(app_mapping.keys()))

# User enters their username
username = st.text_input("Enter Username")

# Button to check access
if st.button("Check Access"):
    if username:
        # Get the instance and SQL query for the selected application
        instance = app_mapping[selected_app]["instance"]
        sql_query = app_mapping[selected_app]["sql_query"]
        
        # Check user access
        has_access = check_user_access(instance, sql_query, username)
        
        # Display the result
        if has_access:
            st.success(f"User '{username}' has access to {selected_app}.")
        else:
            st.error(f"User '{username}' does not have access to {selected_app}.")
    else:
        st.warning("Please enter a username.")