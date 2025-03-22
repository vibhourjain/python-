import win32com.client


def list_outlook_mailboxes():
    # Connect to Outlook
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")

    # List all top-level folders (configured mailboxes)
    mailboxes = []
    for folder in outlook.Folders:
        mailboxes.append(folder.Name)

    return mailboxes


if __name__ == "__main__":
    mailboxes = list_outlook_mailboxes()
    print("Configured Outlook Mailboxes:")
    for idx, name in enumerate(mailboxes, 1):
        print(f"{idx}. {name}")