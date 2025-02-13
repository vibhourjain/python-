import streamlit as st
import pandas as pd
from email_sender import send_email  # Import email function

# **Title**
st.title("📧 Send Email with Table")

# **Input Fields**
to_list = st.text_area("To (comma-separated)", placeholder="email1@example.com, email2@example.com").split(",")
cc_list = st.text_area("CC (comma-separated)", placeholder="email3@example.com, email4@example.com").split(",")
subject = st.text_input("Subject", "Your Subject Here")

# **Create Table for 9 Fields**
st.subheader("Enter Table Data")
columns = ["Field1", "Field2", "Field3", "Field4", "Field5", "Field6", "Field7", "Field8", "Field9"]
data = {col: st.text_input(col, "") for col in columns}
df = pd.DataFrame([data])  # Convert to DataFrame

# **Convert Table to HTML**
table_html = df.to_html(index=False, border=1)

# **Email Body**
body = st.text_area("Additional Message", "Please find the details below:")

# **Complete Email Content**
email_body = f"""
<html>
<head>
    <style>
        table, th, td {{ border: 1px solid black; border-collapse: collapse; padding: 8px; }}
    </style>
</head>
<body>
    <p>{body}</p>
    {table_html}
</body>
</html>
"""

# **Send Email Button**
if st.button("Send Email"):
    if to_list and subject.strip():
        result = send_email(to_list, cc_list, subject, email_body)
        st.success(result)
    else:
        st.error("Please enter recipients and subject.")
