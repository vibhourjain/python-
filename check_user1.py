import streamlit as st
import pyodbc

# Define the mapping of applications to Sybase instances and SQL queries
app_mapping = {
    "App1": {
        "instance": "SybaseInstance1",
        "sql_query": "SELECT uid FROM dbc..CbUser WHERE lower(uid) IN ({})"
    },
    "App2": {
        "instance": "SybaseInstance2",
        "sql_query": "SELECT uid FROM dbc..CbUser WHERE lower(uid) IN ({})"
    },
    # Add mappings for App3, App4, and App5
}

# Function to check user access
def check_user_access(instance, sql_query, usernames):
    try:
        # Connect to the Sybase instance (replace with your connection details)
        conn = pyodbc.connect(
            f"DRIVER={{Sybase}};SERVER={instance};DATABASE=your_db;UID=your_user;PWD=your_password"
        )
        cursor = conn.cursor()
        
        # Format the SQL query with the usernames
        formatted_query = sql_query.format(", ".join(["?"] * len(usernames)))
        
        # Execute the SQL query with the provided usernames
        cursor.execute(formatted_query, usernames)
        results = cursor.fetchall()
        
        # Close the connection
        cursor.close()
        conn.close()
        
        # Return the list of users found in the database
        return [row.uid for row in results]
    except Exception as e:
        st.error(f"Error checking user access: {e}")
        return []

# Streamlit app
st.title("User Access Check")

# User selects the application
selected_app = st.selectbox("Select Application", list(app_mapping.keys()))

# User enters usernames (comma-separated)
user_input = st.text_input("Enter Usernames (comma-separated)")

# Button to check access
if st.button("Check Access"):
    if user_input:
        # Split the input into a list of usernames and convert to lowercase
        usernames = [username.strip().lower() for username in user_input.split(",")]
        
        # Get the instance and SQL query for the selected application
        instance = app_mapping[selected_app]["instance"]
        sql_query = app_mapping[selected_app]["sql_query"]
        
        # Check user access
        found_users = check_user_access(instance, sql_query, usernames)
        
        # Display the results
        if found_users:
            st.success(f"The following users have access to {selected_app}: {', '.join(found_users)}")
        else:
            st.error("No users found with access.")
    else:
        st.warning("Please enter at least one username.")
        
        

v1



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