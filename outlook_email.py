import win32com.client

def send_email(to_list, cc_list, subject, body_html):
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # 0 = Mail Item
    
    mail.To = ";".join(to_list)  # List of recipients
    mail.CC = ";".join(cc_list)  # List of CC recipients
    mail.Subject = subject
    mail.HTMLBody = body_html  # Email body in HTML format

    mail.Send()
    return "Email sent successfully!"
