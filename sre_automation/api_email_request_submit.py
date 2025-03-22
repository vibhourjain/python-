from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import win32com.client
import streamlit as st
import requests

# Simulating a storage for pending requests
pending_requests = {}

app = FastAPI()

def run_powerbroker_command(hostname, fu, fp, fcmd, fotp):
    # Simulate command execution
    return f"Executed command {fcmd} on {hostname} with user {fu}"

def send_email(to_email, request_id):
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = to_email
    mail.Subject = "Powerbroker Request - Action Required"
    mail.Body = f"You have received a Powerbroker request. Please provide credentials using the request ID: {request_id}"
    mail.Send()

class UserARequest(BaseModel):
    hostname: str
    fcmd: str
    email: str  # Email of User B

class UserBRequest(BaseModel):
    request_id: str
    fu: str
    fp: str
    fotp: str

@app.post("/request")
def create_request(user_a: UserARequest):
    request_id = str(uuid.uuid4())
    pending_requests[request_id] = {"hostname": user_a.hostname, "fcmd": user_a.fcmd, "fu": None, "fp": None, "fotp": None}
    
    # Send email notification to User B
    send_email(user_a.email, request_id)
    
    return {"message": "Request created and email sent", "request_id": request_id}

@app.post("/supply")
def supply_credentials(user_b: UserBRequest):
    if user_b.request_id not in pending_requests:
        raise HTTPException(status_code=404, detail="Request not found")
    
    request_data = pending_requests[user_b.request_id]
    request_data["fu"] = user_b.fu
    request_data["fp"] = user_b.fp
    request_data["fotp"] = user_b.fotp
    
    # Check if all required data is available
    if None not in request_data.values():
        result = run_powerbroker_command(**request_data)
        del pending_requests[user_b.request_id]  # Clean up
        return {"message": "Command executed", "result": result}
    
    return {"message": "Credentials received, waiting for other inputs"}

# Streamlit UI for User A to create request
st.title("Powerbroker Request System")

option = st.selectbox("Select Role", ["User A - Create Request", "User B - Supply Credentials"])

if option == "User A - Create Request":
    hostname = st.text_input("Hostname")
    fcmd = st.text_input("Command")
    email = st.text_input("User B Email")
    
    if st.button("Submit Request"):
        response = requests.post("http://localhost:8000/request", json={"hostname": hostname, "fcmd": fcmd, "email": email})
        st.write(response.json())

if option == "User B - Supply Credentials":
    request_id = st.text_input("Request ID")
    fu = st.text_input("FU")
    fp = st.text_input("FP", type="password")
    fotp = st.text_input("FOTP", type="password")
    
    if st.button("Submit Credentials"):
        response = requests.post("http://localhost:8000/supply", json={"request_id": request_id, "fu": fu, "fp": fp, "fotp": fotp})
        st.write(response.json())
