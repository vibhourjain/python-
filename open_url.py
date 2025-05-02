import streamlit as st
import streamlit.components.v1 as components

st.title("Open Ticket in New Tab")

ticket_number = st.text_input("Enter Ticket Number (e.g., WO123455):")

if st.button("Open Ticket"):
    if ticket_number:
        url = f"https://www.vibhour.com/apse/search/{ticket_number}"
        components.html(
            f"""
            <script>
            window.open("{url}", "_blank");
            </script>
            """,
            height=0,
        )
    else:
        st.warning("Please enter a valid ticket number.")
