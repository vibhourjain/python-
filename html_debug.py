import win32com.client as win32
import os

outlook = win32.Dispatch('outlook.application')
mail = outlook.CreateItem(0)

# SEND TO

mail.To = 'Email here'

# SUBJECT

mail.Subject = 'Subject here'

# MESSAGE BODY

mail.HTMLBody = r"""
    The following stuff is ready: <br><br>

    <b>Name</b><br>          //This is the block of code I want to repeat X times.
    Tracking #/ WO #: <br>
    Item #: <br>
    Lot #: <br>
    X containers <br><br>    //This is the end of the repeatable block

    Best regards, <br><br>

    <p style="font-family: Arial; font-size: 10pt"><b>My Name</b><br>
    Title<br>
    Company<br>
    D: phone number here<br>
    fakeEmail@somedomain.com<br>
    www.fakesite.com<br></p>

"""

mail.Save()
