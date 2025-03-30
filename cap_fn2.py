import duckdb


def add_primary_key():
    conn = duckdb.connect(db_path)

    try:
        # Check for duplicates
        duplicates = conn.execute("""
            SELECT hire_date FROM (
                SELECT hire_date, COUNT(*) AS cnt
                FROM table_MADMACS
                GROUP BY hire_date
            ) WHERE cnt > 1
        """).fetchall()

        if duplicates:
            raise ValueError(f"Duplicate hire_dates found: {duplicates}")

        # Create new table with primary key
        conn.execute("""
            CREATE TABLE new_table_MADMACS (
                hire_date DATE PRIMARY KEY,
                employee_cnt INTEGER
            )
        """)

        # Copy data
        conn.execute("""
            INSERT INTO new_table_MADMACS
            SELECT * FROM table_MADMACS
        """)

        # Swap tables
        conn.execute("DROP TABLE table_MADMACS")
        conn.execute("ALTER TABLE new_table_MADMACS RENAME TO table_MADMACS")

        print("Primary key added successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")
        conn.rollback()
    finally:
        conn.close()


# Usage
add_primary_key('capacity_planning_v3.duckdb')