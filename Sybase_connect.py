import pyodbc

# Define Sybase connection parameters
SERVER = "your_sybase_server"
PORT = "5000"  # Change if needed
DATABASE = "your_database"
USERNAME = "your_username"
PASSWORD = "your_password"
DRIVER = "Sybase ASE ODBC Driver"  # Ensure this driver is installed

# Corrected connection string
conn_str = f"""
DRIVER={{{DRIVER}}};
SERVER={SERVER};
PORT={PORT};
DATABASE={DATABASE};
UID={USERNAME};
PWD={PASSWORD};
"""

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Example query
    query = "SELECT TOP 10 * FROM your_table;"
    cursor.execute(query)

    # Fetch and print results
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    # Close connection
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
