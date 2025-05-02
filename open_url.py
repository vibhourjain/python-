import streamlit as st

# Title
st.title("Ticket Search")

# Ticket input
ticket_number = st.text_input("Enter Ticket Number (e.g., WO123455):")

# Submit button
if st.button("Open Ticket"):
    if ticket_number:
        url = f"https://www.vibhour.com/apse/search/{ticket_number}"
        # JavaScript to open in new tab
        js = f"""
        <script>
        window.open("{url}", "_blank").focus();
        </script>
        """
        st.markdown(js, unsafe_allow_html=True)
    else:
        st.warning("Please enter a valid ticket number.")
