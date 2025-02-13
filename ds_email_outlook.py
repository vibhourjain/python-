def page_seek_approval():
    st.title("Seek Approval Form")

    # Define the list of applications for the dropdown
    application_name = ["OSCAR", "PETA", "MADMACS"]
    application_name.sort()  # Sort the list alphabetically

    # Define the fields for the table
    field_labels = [
        "Incident Number",
        "Impacted Application",
        "Business Justification",
        "Latent Defect Details",
        "Proposed Fix",
        "Risk if Not Fixed",
        "MAPS Lead Approval",
        "Target Date for Fix",
        "Comments",
    ]

    # Create a dictionary to store field values
    field_values = {}

    # Display input fields
    for label in field_labels:
        if label == "Impacted Application":
            # Dropdown for Impacted Application
            field_values[label] = st.selectbox(label, application_name)
        elif label == "MAPS Lead Approval":
            # Editable field with default value
            field_values[label] = st.text_input(label, value="sachin.patil@jpmc.com")
        else:
            # Regular text input for other fields
            field_values[label] = st.text_input(label)

    # Email subject is always "Incident Number - Latent Approval Request"
    email_subject = f"{field_values['Incident Number']} - Latent Approval Request"

    # Display email details in an expander
    with st.expander("Email Details"):
        to_list = st.text_area("To (comma-separated):").split(",")
        cc_list = st.text_area("CC (comma-separated):").split(",")
        from_email = st.text_input("From (your email):")

        # Validate email domains for "To" and "CC" lists
        def validate_email_domain(email_list, domain="jpmc.com"):
            invalid_emails = [email.strip() for email in email_list if not email.strip().endswith(f"@{domain}")]
            if invalid_emails:
                st.error(f"The following emails are not from the {domain} domain: {', '.join(invalid_emails)}")
                return False
            return True

        # Preview email body
        email_body = "<h3>Latent Request Approval</h3><table border='1'>" + "".join(
            f"<tr><td>{key}</td><td>{value}</td></tr>" for key, value in field_values.items()
        ) + "</table>"

        st.write("Preview of Email Body:")
        st.markdown(email_body, unsafe_allow_html=True)

        # Send email button
        if st.button("Send Email"):
            # Validate email domains
            if validate_email_domain(to_list) and validate_email_domain(cc_list):
                send_email(to_list, cc_list, email_subject, from_email, email_body)
