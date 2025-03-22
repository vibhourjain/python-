import streamlit as st
import pandas as pd
import os
from datetime import datetime

def feedback_component():
    """Feedback component with edit capabilities"""
    
    # Configuration
    CSV_FILE = "feedback.csv"
    COLUMNS = ["ID", "Timestamp", "Requestor", "Details", "Status", "Resolution"]
    
    # Initialize session state
    if 'edit_id' not in st.session_state:
        st.session_state.edit_id = None
    
    # Initialize CSV
    if not os.path.exists(CSV_FILE):
        pd.DataFrame(columns=COLUMNS).to_csv(CSV_FILE, index=False)

    def get_next_id():
        df = pd.read_csv(CSV_FILE)
        return f"ADO-{len(df) + 1:04d}"

    def save_feedback(requestor, details):
        new_entry = {
            "ID": get_next_id(),
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Requestor": requestor,
            "Details": details,
            "Status": "Open",
            "Resolution": ""
        }
        pd.DataFrame([new_entry]).to_csv(CSV_FILE, mode='a', header=False, index=False)

    def update_feedback(feedback_id, requestor, details, status, resolution):
        df = pd.read_csv(CSV_FILE)
        idx = df.index[df['ID'] == feedback_id].tolist()[0]
        
        df.at[idx, 'Requestor'] = requestor
        df.at[idx, 'Details'] = details
        df.at[idx, 'Status'] = status
        df.at[idx, 'Resolution'] = resolution
        
        df.to_csv(CSV_FILE, index=False)
        st.session_state.edit_id = None  # Reset edit mode

    # Page layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Submit Feedback")
        with st.form("feedback_form"):
            requestor = st.text_input("Requestor Name")
            details = st.text_area("Feedback Details")
            submitted = st.form_submit_button("Submit")
            
            if submitted:
                if requestor and details:
                    save_feedback(requestor, details)
                    st.success("Feedback submitted!")
                    st.rerun()
                else:
                    st.warning("Please fill both fields")

    with col2:
        st.subheader("Existing Feedback")
        
        try:
            df = pd.read_csv(CSV_FILE)
            
            if st.session_state.edit_id:
                # Edit form for selected feedback
                selected = df[df['ID'] == st.session_state.edit_id].iloc[0]
                
                with st.form("edit_form"):
                    st.write(f"Editing: {selected['ID']}")
                    new_requestor = st.text_input("Requestor", value=selected['Requestor'])
                    new_details = st.text_area("Details", value=selected['Details'])
                    new_status = st.selectbox(
                        "Status",
                        ["Open", "In Progress", "Resolved"],
                        index=["Open", "In Progress", "Resolved"].index(selected['Status'])
                    )
                    new_resolution = st.text_area("Resolution", value=selected['Resolution'])
                    
                    if st.form_submit_button("Update Feedback"):
                        update_feedback(
                            st.session_state.edit_id,
                            new_requestor,
                            new_details,
                            new_status,
                            new_resolution
                        )
                        st.success("Feedback updated!")
                        st.rerun()
                        
                    if st.form_submit_button("Cancel"):
                        st.session_state.edit_id = None
                        st.rerun()
            
            else:
                # Display feedback list
                for _, row in df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**ID:** {row['ID']} | **Status:** {row['Status']}")
                        st.caption(f"Submitted on: {row['Timestamp']} by {row['Requestor']}")
                        st.write(row['Details'])
                        if row['Resolution']:
                            st.success(f"Resolution: {row['Resolution']}")
                        
                        if st.button("Edit", key=f"edit_{row['ID']}"):
                            st.session_state.edit_id = row['ID']
                            st.rerun()
                
                if df.empty:
                    st.info("No feedback submitted yet")

        except Exception as e:
            st.error(f"Error loading feedback: {str(e)}")

        if st.button("Refresh List"):
            st.rerun()
