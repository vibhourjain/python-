import streamlit as st
import pandas as pd
import io
import datetime

def page_multi_sql():
    st.title("Run Multiple SQL Files and Export to Excel")

    start_date = st.date_input("Select Start Date")
    end_date = st.date_input("Select End Date")

    if st.button("Run Queries"):
        if not start_date or not end_date:
            st.error("Please select both start and end dates.")
        else:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                for instance, details in sql_files.items():
                    sql_file_path = details["file"]
                    sheet_name = details["sheet_name"]

                    st.write(f"Executing SQL for **{instance}**...")

                    try:
                        # Read SQL file once
                        with open(sql_file_path, "r", encoding="utf-8") as file:
                            sql_query = file.read()

                        conn = connect_to_sybase(instance)
                        if conn:
                            df = execute_query(
                                conn, 
                                sql_query, 
                                start_date.strftime('%Y-%m-%d'), 
                                end_date.strftime('%Y-%m-%d')
                            )
                            if df is not None and not df.empty:
                                # Ensure Japanese characters are handled properly
                                df.to_excel(writer, sheet_name=sheet_name, index=False)
                                st.success(f"Results saved for {instance} ✅")
                            else:
                                st.warning(f"No data returned for {instance} ⚠️")

                            conn.close()

                    except Exception as e:
                        st.error(f"Error processing {instance}: {e}")
                        continue  # Continue to the next instance even if one fails

            # Ensure buffer is set to the beginning before downloading
            excel_buffer.seek(0)

            # Streamlit download button with proper encoding
            st.download_button(
                label="Download Excel File",
                data=excel_buffer.getvalue(),  # Ensure data is correctly fetched
                file_name=f"query_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
