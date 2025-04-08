import duckdb

# Paths to your DuckDB database files
new_db_path = 'new_database.duckdb'  # Path to your new DuckDB database
old_db_path = 'old_database.duckdb'  # Path to your old DuckDB database

# Connect to the new DuckDB database
conn = duckdb.connect(new_db_path)

# Attach the old DuckDB database with an alias, e.g., 'old_db'
conn.execute(f"ATTACH '{old_db_path}' AS old_db;")

# Define the schema and table names
schema_name = 'capacity_planning'
table_name = 'your_table_name'  # Replace with your actual table name

# Insert data from the old database's table into the existing table in the new database
conn.execute(f"""
    INSERT INTO {schema_name}.{table_name}
    SELECT * FROM old_db.{schema_name}.{table_name};
""")

# Detach the old database
conn.execute("DETACH old_db;")

# Commit and close the connection
conn.commit()
conn.close()
