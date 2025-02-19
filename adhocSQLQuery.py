import streamlit as st
import pandas as pd
import io

def page_sql():
    st.title("SQL Query Runner")

    # Text area for SQL input
    sql_query = st.text_area("Paste your SQL query here:", height=150)

    # Buttons for selecting the instance
    instance_buttons = ["Instance 1", "Instance 2", "Instance 3", "Instance 4", "Instance 5"]
    selected_instance = st.radio("Select an Instance", instance_buttons)

    if st.button("Run Query"):
        if sql_query.strip() == "":
            st.warning("Please enter a SQL query.")
        else:
            with st.spinner(f"Running query on {selected_instance}..."):
                conn = connect_to_sybase(selected_instance)
                if conn:
                    df = execute_query(conn, sql_query)
                    conn.close()

                    if df is not None and not df.empty:
                        total_records = len(df)  # Count total records
                        st.success(f"Query executed successfully! ✅ Total records fetched: **{total_records}**")
                        st.write(f"### Preview (Top 10 results from {selected_instance}):")
                        st.dataframe(df.head(10))  # Display top 10 rows
                        st.session_state["result_df"] = df
                        st.session_state["total_records"] = total_records
                    else:
                        st.warning("No data returned from the query.")

    # Display total record count if available
    if "total_records" in st.session_state:
        st.write(f"**Total Records Fetched:** {st.session_state['total_records']}")

    # Download Results as Excel
    if "result_df" in st.session_state:
        st.write("### Download Results as Excel")
        
        file_name = st.text_input("Enter the file name (without extension):", "query_results")

        if st.button("Download Excel"):
            if file_name.strip() == "":
                st.warning("Please enter a valid file name.")
            else:
                # Create an in-memory buffer
                excel_buffer = io.BytesIO()

                # Write DataFrame to Excel with utf-8-sig encoding for Japanese support
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    st.session_state["result_df"].to_excel(writer, sheet_name="Results", index=False)

                # Reset buffer position for download
                excel_buffer.seek(0)

                # Download button for user
                st.download_button(
                    label="Download Excel File",
                    data=excel_buffer,
                    file_name=f"{file_name}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
