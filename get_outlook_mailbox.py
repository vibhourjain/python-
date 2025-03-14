import win32com.client

def list_outlook_mailboxes():
    try:
        # Connect to Outlook
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")

        # Get all mailboxes
        mailboxes = [namespace.Folders.Item(i+1).Name for i in range(namespace.Folders.Count)]

        print("Configured Mailboxes in Outlook:")
        for idx, mailbox in enumerate(mailboxes, start=1):
            print(f"{idx}. {mailbox}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_outlook_mailboxes()