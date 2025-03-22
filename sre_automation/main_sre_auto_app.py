import streamlit as st
import logging
import os
import page_interactive_unix

logger = logging.getLogger(__name__)
log_file_name =os.path.expanduser("~/python_app.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file_name,
    encoding='utf-8',
    filemode='a'
)

def page_payment_tasks():
    st.write("Payment Team Tasks")

def page_sales_tasks():
    task_page = st.sidebar.radio("Select a Task",
                                     ["Information",
                                      "Adhoc SQL Report",
                                      "Remote Unix Command Executor",
                                      "Monthly Tasks",
                                      "Approval Template",
                                      "User Access"]
                                     )

    if page == "Adhoc SQL Report":
        page_adhoc_sql_report()
    elif page == "Remote Unix Command Executor":
        page_ssh()
    elif page == "Approval Template":
        page_approval_template()
    elif page == "Monthly Task":
        page_monthly_tasks()
    elif page == "User Access":
        page_user_access()
    elif page == "Information":
        page_information()
    elif page == "Unix Strikes":
        page_unix_strikes()


def page_adhoc_sql_report():
    pass

def page_ssh():
    pass

def page_approval_template():
    pass

def page_monthly_tasks():
    pass

def page_user_access():
    pass

def page_information():
    pass

def page_unix_strikes():
    page_interactive_unix.page_interactive_broker()

def main():
    st.sidebar.title("SRE Automation")
    logger.info('Application Started')

    page= st.sidebar.radio("Home Cabinets Team",["Sales Team","Payment Teams"])

    if page == "Sales Team":
        logger.info("Jumping to Sales Team")
        page_sales_tasks()
    elif page == "Payment Team":
        logger.info("Jumping to Payment Team")
        page_payment_tasks()

if __name__ == "__main__":
    main()
