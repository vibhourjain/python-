import streamlit as st
import pandas as pd
import io

def page_sql():
    st.title("SQL Query Runner")

    sql_query = st.text_area("Paste your SQL query here:", height=150)

    instance_buttons = ["Instance 1", "Instance 2", "Instance 3", "Instance 4", "Instance 5"]
    selected_instance = st.radio("Select an instance", instance_buttons)

    if st.button("Run Query"):
        if sql_query.strip() == "":
            st.warning("Please enter a SQL query.")
        else:
            with st.spinner(f"Running query on {selected_instance}..."):
                conn = connect_to_sybase(selected_instance)
                if conn:
                    df = execute_query(conn, sql_query, "2024-01-01", "2024-12-31")
                    if df is not None:
                        st.success("Query executed successfully!")
                        st.write(f"Top 10 results from {selected_instance}:")
                        st.dataframe(df.head(10))
                        conn.close()
                        st.session_state["result_df"] = df  # Store result in session state

    # Allow download only if there's a result
    if "result_df" in st.session_state:
        st.write("### Save Results to Excel")
        file_name = st.text_input("Enter the file name (without extension):", "output")

        # Generate file only when the download button is clicked
        if st.button("Generate Excel File"):
            if file_name.strip() == "":
                st.warning("Please enter a valid file name.")
            else:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    st.session_state["result_df"].to_excel(writer, sheet_name="Results", index=False)
                output.seek(0)

                # Save file in session state (avoids reprocessing when clicking download)
                st.session_state["excel_file"] = output

                st.success("Excel file generated! Click the button below to download.")

        # Only show download button if file is generated
        if "excel_file" in st.session_state:
            st.download_button(
                label="Download Excel File",
                data=st.session_state["excel_file"],
                file_name=f"{file_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
