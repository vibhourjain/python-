import streamlit as st
import pandas as pd
from datetime import datetime
import os

# File path for storing feedback
FEEDBACK_FILE = "feedback_data.csv"

# Initialize feedback data
if not os.path.exists(FEEDBACK_FILE):
    pd.DataFrame(columns=['Timestamp', 'Submitted_By', 'Details', 'Status', 'Remarks']).to_csv(FEEDBACK_FILE, index=False)

def save_feedback(data):
    """Save feedback to CSV file"""
    df = pd.DataFrame([data])
    df.to_csv(FEEDBACK_FILE, mode='a', header=False, index=False)

def load_feedback():
    """Load feedback from CSV file"""
    return pd.read_csv(FEEDBACK_FILE)

def update_feedback(row_index, remarks, status):
    """Update feedback status and remarks"""
    df = load_feedback()
    if row_index < len(df):
        df.at[row_index, 'Remarks'] = remarks
        df.at[row_index, 'Status'] = status
        df.to_csv(FEEDBACK_FILE, index=False)
        return True
    return False

# Page configuration
st.set_page_config(page_title="Feedback Management System", layout="wide")

# Main header
st.title("📝 Real-Time Feedback Management System")
st.markdown("---")

# Feedback submission form
with st.form("feedback_form"):
    st.subheader("Submit New Feedback")
    col1, col2 = st.columns(2)
    
    with col1:
        submitted_by = st.text_input("Your Name/Email")
        details = st.text_area("Feedback Details", height=100)
    
    with col2:
        status = st.selectbox("Initial Status", ["Open", "In Progress", "Resolved"])
        remarks = st.text_input("Initial Remarks (optional)")
    
    submitted = st.form_submit_button("Submit Feedback")
    
    if submitted:
        if submitted_by and details:
            new_feedback = {
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'Submitted_By': submitted_by,
                'Details': details,
                'Status': status,
                'Remarks': remarks
            }
            save_feedback(new_feedback)
            st.success("Feedback submitted successfully!")
        else:
            st.warning("Please fill in required fields (Name/Email and Details)")

# Display and manage feedback
st.markdown("---")
st.subheader("Feedback Dashboard")

# Load and display feedback
feedback_df = load_feedback()

if not feedback_df.empty:
    # Add update functionality
    for index, row in feedback_df.iterrows():
        with st.expander(f"Feedback #{index+1} - {row['Status']}"):
            col1, col2, col3 = st.columns([2,3,2])
            
            with col1:
                st.markdown(f"**Submitted By:** {row['Submitted_By']}")
                st.markdown(f"**Date:** {row['Timestamp']}")
                st.markdown(f"**Current Status:** {row['Status']}")
                
            with col2:
                st.markdown("**Details:**")
                st.info(row['Details'])
                
            with col3:
                with st.form(key=f"update_form_{index}"):
                    new_status = st.selectbox(
                        "Update Status",
                        ["Open", "In Progress", "Resolved"],
                        index=["Open", "In Progress", "Resolved"].index(row['Status']),
                        key=f"status_{index}"
                    )
                    new_remarks = st.text_input(
                        "Update Remarks",
                        value=row['Remarks'],
                        key=f"remarks_{index}"
                    )
                    if st.form_submit_button("Update"):
                        if update_feedback(index, new_remarks, new_status):
                            st.experimental_rerun()
else:
    st.info("No feedback submissions yet.")

# Add real-time refresh
st.markdown("---")
if st.button("Refresh Feed"):
    st.experimental_rerun()

# Optional: Add statistics
if not feedback_df.empty:
    st.markdown("### Feedback Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Feedback", len(feedback_df))
        
    with col2:
        status_counts = feedback_df['Status'].value_counts()
        st.write("Status Distribution:")
        st.dataframe(status_counts)
        
    with col3:
        latest_feedback = feedback_df.iloc[-1]
        st.write("Latest Feedback:")
        st.code(f"By: {latest_feedback['Submitted_By']}\n"
                f"Status: {latest_feedback['Status']}\n"
                f"Date: {latest_feedback['Timestamp']}")