import streamlit as st
import duckdb


def create_metadata_table():
    conn = duckdb.connect("capacity_planning.duckdb")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS metadata (
                        application_name TEXT PRIMARY KEY,
                        table_name TEXT UNIQUE,
                        sql_query TEXT
                      )''')
    conn.commit()
    conn.close()


def create_application_table(app_name, columns):
    conn = duckdb.connect("capacity_planning.duckdb")
    cursor = conn.cursor()
    table_name = f"table_{app_name}"

    # Check if table exists
    cursor.execute("SELECT table_name FROM metadata WHERE table_name=?", (table_name,))
    if cursor.fetchone():
        st.error(f"Table for application {app_name} already exists!")
        conn.close()
        return

    column_definitions = ", ".join([f"{col['name']} {col['type']}" for col in columns])
    sql = f"CREATE TABLE {table_name} ({column_definitions})"

    cursor.execute(sql)
    cursor.execute("INSERT INTO metadata (application_name, table_name, sql_query) VALUES (?, ?, ?)",
                   (app_name, table_name, ""))

    conn.commit()
    conn.close()
    st.success(f"Table {table_name} created successfully!")


def view_metadata():
    conn = duckdb.connect("capacity_planning.duckdb")
    df = conn.execute("SELECT * FROM metadata").fetchdf()

    metadata_details = []
    for index, row in df.iterrows():
        table_name = row['table_name']
        columns_df = conn.execute(f"PRAGMA table_info({table_name})").fetchdf()
        columns_list = ", ".join(columns_df['name'].tolist()) if not columns_df.empty else "No columns found"
        metadata_details.append({
            "Application Name": row['application_name'],
            "Table Name": row['table_name'],
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
        conn = duckdb.connect("capacity_planning.duckdb")
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
        conn = duckdb.connect("capacity_planning.duckdb")
        table_name = f"table_{app_name}"
        try:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_col_name} {new_col_type}")
            st.success(f"Column {new_col_name} added to {table_name}")
        except Exception as e:
            st.error(f"Error: {e}")
        conn.close()


def modify_metadata():
    st.write("### Modify Metadata Table")
    column_name = st.text_input("Enter New Column Name")
    column_type = st.selectbox("Select Data Type", ["TEXT", "INTEGER", "DOUBLE", "DATE"])

    if st.button("Add Column to Metadata"):
        conn = duckdb.connect("capacity_planning.duckdb")
        try:
            conn.execute(f"ALTER TABLE metadata ADD COLUMN {column_name} {column_type}")
            st.success(f"Column {column_name} added to metadata table")
        except Exception as e:
            st.error(f"Error: {e}")
        conn.close()


def main():
    st.title("Capacity Planning - Database Setup")
    create_metadata_table()

    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Go to", ["Create Table", "View Metadata", "Query Tables", "Alter Table","Modify Metadata"])

    if page == "Create Table":
        st.header("Create New Application Table")
        app_name = st.text_input("Enter Application Name")

        columns = []
        if "columns" not in st.session_state:
            st.session_state.columns = []

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
            if app_name and st.session_state.columns:
                create_application_table(app_name, st.session_state.columns)
                st.session_state.columns = []
            else:
                st.error("Enter application name and at least one column.")

    elif page == "View Metadata":
        view_metadata()

    elif page == "Query Tables":
        query_table()

    elif page == "Alter Table":
        alter_table()

    elif page == "Modify Metadata":
        modify_metadata()


if __name__ == "__main__":
    main()

