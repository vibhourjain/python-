import streamlit as st
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(filename="issue_tracking.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Define file storage path
STORAGE_DIR = "/server/issue_logs"  # Update the correct path
FILE_PATH = os.path.join(STORAGE_DIR, "issue_records.csv")

# Ensure directory exists
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR)

# Expected CSV columns
EXPECTED_COLUMNS = ["Application Name", "Issue Description", "Efforts"]

# **Function to append a record manually**
def append_manual_record(app_name, issue_desc, efforts):
    """Appends manually entered issue details to the file."""
    df = pd.DataFrame([[app_name, issue_desc, efforts]], columns=EXPECTED_COLUMNS)

    if os.path.exists(FILE_PATH):
        df.to_csv(FILE_PATH, mode="a", index=False, header=False)  # Append without header
    else:
        df.to_csv(FILE_PATH, index=False)  # Create new file

    logging.info(f"Manually added issue: {app_name}, {issue_desc}, {efforts}")
    st.success("Issue logged successfully!")

# **Function to save uploaded file**
def save_uploaded_file(uploaded_file):
    """Saves uploaded file temporarily."""
    temp_path = os.path.join(STORAGE_DIR, uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

# **Function to validate and append uploaded data**
def validate_and_append(file_path):
    """Validates and appends bulk upload data to the file."""
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            st.error("Invalid file format. Please upload CSV or Excel.")
            return

        # Validate columns
        if list(df.columns) != EXPECTED_COLUMNS:
            st.error(f"Invalid column structure. Expected: {EXPECTED_COLUMNS}")
            return

        # Append to the master file
        if os.path.exists(FILE_PATH):
            df.to_csv(FILE_PATH, mode="a", index=False, header=False)
        else:
            df.to_csv(FILE_PATH, index=False)

        st.success(f"Successfully added {len(df)} issues to the log.")
        logging.info(f"Bulk uploaded {len(df)} records.")

    except Exception as e:
        st.error(f"Error processing file: {e}")
        logging.error(f"File upload error: {e}")

# **Function to display last record**
def display_last_record():
    """Displays the last record from the file."""
    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
        if not df.empty:
            st.subheader("📌 Last Logged Issue:")
            st.dataframe(df.tail(1))
        else:
            st.info("No records found.")
    else:
        st.info("No records found.")

# **Streamlit UI**
st.title("📝 Issue Logging System")

tab1, tab2 = st.tabs(["✍️ Manual Entry", "📂 Bulk Upload"])

# **Tab 1: Manual Entry**
with tab1:
    st.subheader("Log a New Issue")

    app_name = st.selectbox("Application Name", ["abc", "efg"])
    issue_desc = st.text_area("Issue Description")
    efforts = st.text_input("Efforts (in hours)")

    if st.button("Submit Issue"):
        if issue_desc and efforts:
            append_manual_record(app_name, issue_desc, efforts)
        else:
            st.warning("Please fill all fields.")

# **Tab 2: Bulk Upload**
with tab2:
    st.subheader("Upload Issue Records")

    uploaded_file = st.file_uploader("Upload CSV/Excel file", type=["csv", "xlsx"])

    if uploaded_file and st.button("Upload and Append"):
        file_path = save_uploaded_file(uploaded_file)
        validate_and_append(file_path)

# **Display last record after submission/upload**
display_last_record()
