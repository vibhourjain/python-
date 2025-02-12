import streamlit as st
from utils.db_utils import connect_to_sybase, execute_query

def page_monthly_task():
    st.title("Monthly Task")

    # Sidebar to select subpage
    task_page = st.sidebar.radio("Select a Report", ["Cash Report", "Journal Report"])

    if task_page == "Cash Report":
        cash_report()
    elif task_page == "Journal Report":
        journal_report()

# Cash Report Page
def cash_report():
    st.subheader("Cash Report")

    # Date input for cash report
    date = st.date_input("Select Date for Cash Report")

    if st.button("Run Cash Report"):
        sql_query = """
        SELECT *
        FROM cash_report
        WHERE report_date = '{date}';
        """.format(date=date.strftime('%Y-%m-%d'))
        
        conn = connect_to_sybase("Instance 1")  # You can choose the instance
        if conn:
            df = execute_query(conn, sql_query)
            if df is not None:
                st.success("Cash Report executed successfully!")
                st.dataframe(df)

# Journal Report Page
def journal_report():
    st.subheader("Journal Report")

    # Parameters for journal report
    journal_id = st.text_input("Enter Journal ID")
    start_date = st.date_input("Start Date for Journal Report")
    end_date = st.date_input("End Date for Journal Report")

    if st.button("Run Journal Report"):
        if journal_id and start_date and end_date:
            sql_query = """
            SELECT *
            FROM journal_report
            WHERE journal_id = '{journal_id}'
            AND report_date BETWEEN '{start_date}' AND '{end_date}';
            """.format(
                journal_id=journal_id,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            conn = connect_to_sybase("Instance 2")  # You can choose the instance
            if conn:
                df = execute_query(conn, sql_query)
                if df is not None:
                    st.success("Journal Report executed successfully!")
                    st.dataframe(df)
        else:
            st.warning("Please provide all inputs for the Journal Report.")
