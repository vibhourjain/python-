import streamlit as st
import duckdb

DB_PATH = r"C:\Users\vibho\ado-0001\python-\capacity_planning_v3.duckdb"  # Change this path as needed

def create_metadata_table():
    conn = duckdb.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS metadata (
                        application_name TEXT PRIMARY KEY,
                        table_name TEXT UNIQUE,
                        database_name TEXT,
                        sql_query TEXT
                      )''')
    conn.commit()
    conn.close()

def add_column_to_metadata():
    conn = duckdb.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE metadata ADD COLUMN database_name TEXT")
        conn.commit()
        st.success("Column 'database_name' added successfully to metadata table!")
    except Exception as e:
        st.error(f"Error adding column: {e}")

    conn.close()


def create_application_table(app_name, database_name, columns, sql_query):
    conn = duckdb.connect(DB_PATH)
    cursor = conn.cursor()
    table_name = f"table_{app_name}"

    # Check if table exists before creating
    existing_tables = conn.execute("SELECT table_name FROM metadata").fetchdf()
    if table_name in existing_tables['table_name'].values:
        st.error(f"Table {table_name} already exists!")
        conn.close()
        return

    # Create Table
    column_definitions = ", ".join([f"{col['name']} {col['type']}" for col in columns])
    sql = f"CREATE TABLE {table_name} ({column_definitions})"
    cursor.execute(sql)

    # Insert metadata
    cursor.execute("INSERT INTO metadata (application_name, table_name, database_name, sql_query) VALUES (?, ?, ?, ?)",
                   (app_name, table_name, database_name, sql_query))

    conn.commit()
    conn.close()
    st.success(f"Table {table_name} created successfully!")



def view_metadata():
    conn = duckdb.connect(DB_PATH)
    df = conn.execute("SELECT * FROM metadata").fetchdf()

    metadata_details = []
    for index, row in df.iterrows():
        table_name = row['table_name']
        columns_df = conn.execute(f"PRAGMA table_info({table_name})").fetchdf()
        columns_list = ", ".join(columns_df['name'].tolist()) if not columns_df.empty else "No columns found"

        # Check if 'database_name' exists and handle missing values
        database_name = row.get('database_name', 'N/A')  # Default to 'N/A' if column is missing

        metadata_details.append({
            "Application Name": row['application_name'],
            "Table Name": row['table_name'],
            "Database Name": database_name,
            "SQL Query": row['sql_query'],
            "Columns": columns_list
        })

    conn.close()
    st.write("### Metadata Table")
    st.dataframe(metadata_details)


def query_table():
    st.write("### Query Tables")
    query = st.text_area("Enter SQL Query")
    if st.button("Run Query"):
        conn = duckdb.connect(DB_PATH)
        try:
            df = conn.execute(query).fetchdf()
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error: {e}")
        conn.close()


def alter_table():
    st.write("### Alter Table")
    app_name = st.text_input("Enter Application Name")
    new_col_name = st.text_input("New Column Name")
    new_col_type = st.selectbox("Data Type", ["TEXT", "INTEGER", "DOUBLE", "DATE"])
    if st.button("Add Column to Table"):
        conn = duckdb.connect(DB_PATH)
        table_name = f"table_{app_name}"
        try:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_col_name} {new_col_type}")
            st.success(f"Column {new_col_name} added to {table_name}")
        except Exception as e:
            st.error(f"Error: {e}")
        conn.close()

def show_all_tables():
    st.write("### Show all DB Tables")
    query_1=f"show all tables"
    if st.button("Show Tables"):
        conn = duckdb.connect(DB_PATH)
        try:
            df = conn.execute(query_1).fetchdf()
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error: {e}")
        conn.close()

# Function to update sql_query in metadata
def update_sql_query():
    st.write("### Update SQL Query for an Application")
    app_name = st.text_input("Enter Application Name to Update SQL Query")

    if app_name:
        conn = duckdb.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if the application exists in the metadata
        cursor.execute("SELECT sql_query FROM metadata WHERE application_name=?", (app_name,))
        existing_data = cursor.fetchone()

        if existing_data:
            st.write(f"Existing SQL Query: {existing_data[0]}")
            new_sql_query = st.text_area("Enter New SQL Query", value=existing_data[0])

            if st.button("Update SQL Query"):
                cursor.execute("UPDATE metadata SET sql_query=? WHERE application_name=?",
                               (new_sql_query, app_name))
                conn.commit()
                st.success(f"SQL Query for application '{app_name}' updated successfully!")
        else:
            st.error(f"Application '{app_name}' not found in the metadata.")

        conn.close()


# def describe_table_columns():
#     conn = duckdb.connect(DB_PATH)
#     app_list = conn.execute("SELECT application_name FROM metadata").fetchdf()["application_name"].tolist()
#     conn.close()
#
#     if not app_list:
#         st.error("No applications found in metadata.")
#         return
#
#     selected_app = st.selectbox("Select Application", app_list)
#
#     if selected_app:
#         conn = duckdb.connect(DB_PATH)
#         cursor = conn.cursor()
#         cursor.execute("SELECT sql_query FROM metadata WHERE application_name=?", (selected_app,))
#         table_name = cursor.fetchone()
#         conn.close()
#
#
#         conn = duckdb.connect(DB_PATH)
#         # Query to get columns of the specified table
#         query = f"""
#         SELECT column_name, data_type
#         FROM information_schema.columns
#         WHERE table_name = '{table_name}'
#         ORDER BY ordinal_position
#         """
#         # Execute query and get the result
#         columns = conn.execute(query).fetchdf()
#         conn.close()
#
#         if columns.empty:
#             st.error(f"No columns found for table: {table_name}")
#         else:
#             st.write(f"Columns of table `{table_name}`:")
#             st.dataframe(columns)

def describe_table_columns():
    conn = duckdb.connect(DB_PATH)
    table_name = st.text_input("Enter table_name")

    # Query to get columns of the specified table
    query = f"""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = '{table_name}'
    ORDER BY ordinal_position
    """

    # Execute query and get the result
    columns = conn.execute(query).fetchdf()

    conn.close()

    if columns.empty:
        st.error(f"No columns found for table: {table_name}")
    else:
        st.write(f"Columns of table `{table_name}`:")
        st.dataframe(columns)


def main():
    st.title("Capacity Planning - Database Setup")
    create_metadata_table()

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to",
                            ["Create Table", "View Metadata", "Query Tables", "Alter Table", "Update SQL Query","Show All tables","Describe table"])

    if page == "Create Table":
        if "columns" not in st.session_state:
            st.session_state.columns = []  # Ensure session state exists

        st.header("Create New Application Table")
        app_name = st.text_input("Enter Application Name")
        database_name = st.text_input("Enter Database Name")
        sql_query = st.text_area("Enter SQL Query (Use placeholders start_date and end_date)")

        col_name = st.text_input("Column Name")
        col_type = st.selectbox("Data Type", ["TEXT", "INTEGER", "DOUBLE", "DATE"])

        if st.button("Add Column"):
            if col_name in [c['name'] for c in st.session_state.columns]:
                st.error("Column name already exists!")
            else:
                st.session_state.columns.append({"name": col_name, "type": col_type})

        st.write("### Columns:")
        for col in st.session_state.columns:
            st.write(f"- {col['name']} ({col['type']})")

        if st.button("Create Table"):
            if app_name and database_name and sql_query and st.session_state.columns:
                create_application_table(app_name, database_name, st.session_state.columns, sql_query)
                st.session_state.columns = []  # Clear columns after table creation
            else:
                st.error("Enter application name, database name, SQL query, and at least one column.")


    elif page == "View Metadata":
        view_metadata()

    elif page == "Query Tables":
        query_table()

    elif page == "Alter Table":
        alter_table()

    elif page == "Update SQL Query":
        update_sql_query()
    elif page == "Show All tables":
        show_all_tables()
    elif page == "Describe table":
        describe_table_columns()


if __name__ == "__main__":
    main()
