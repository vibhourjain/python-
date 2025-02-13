import streamlit as st
import pandas as pd
import io
from email_sender import send_email_outlook

if "result_df" in st.session_state:
    st.write("### Save & Email Results")

    file_name = st.text_input("Enter file name (without extension):", "query_results")

    if st.button("Write to Excel"):
        if file_name.strip() == "":
            st.warning("Please enter a valid file name.")
        else:
            # Save the DataFrame in memory (not on disk)
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                st.session_state["result_df"].to_excel(writer, index=False)
            excel_data = excel_buffer.getvalue()
            st.success("Results saved in memory!")

            # Show email form
            with st.form("email_form"):
                st.write("### Send Email")
                sender = st.text_input("From:", "your_outlook_email@example.com")
                recipients = st.text_input("To (comma-separated):", "")
                cc = st.text_input("CC (comma-separated, optional):", "")
                subject = st.text_input("Subject:", "Query Results")
                body = st.text_area("Body:", "Please find the attached query results.")

                submitted = st.form_submit_button("Send Email")

                if submitted:
                    recipients_list = [r.strip() for r in recipients.split(",") if r.strip()]
                    cc_list = [c.strip() for c in cc.split(",") if c.strip()]
                    
                    if recipients_list:
                        response = send_email_outlook(
                            sender, recipients_list, cc_list, subject, body,
                            attachment=excel_data, filename=f"{file_name}.xlsx"
                        )
                        st.success(response)
                    else:
                        st.error("Please enter at least one recipient.")
