import os
import requests
import bcrypt 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI()

USER_DATA_URL = os.getenv("USER_DATA_URL", "http://user-data-service:80")

class RegisterPayload(BaseModel):
    email: EmailStr
    password: str
    full_name: str

@app.post("/register")
def register(data: RegisterPayload):
    # 1. Check for duplicates
    try:
        check_resp = requests.get(f"{USER_DATA_URL}/users/{data.email}")
        if check_resp.status_code == 200:
            raise HTTPException(status_code=400, detail="Email already registered")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Data Service Unavailable")

    # Convert string to bytes
    password_bytes = data.password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    
    # Decode back to string so it can be sent as JSON
    hashed_password_str = hashed_bytes.decode('utf-8')

    # 3. Save User
    new_user = {
        "email": data.email,
        "full_name": data.full_name,
        "password_hash": hashed_password_str, # Use the new string
        "favorites": []
    }

    save_resp = requests.post(f"{USER_DATA_URL}/users", json=new_user)

    if save_resp.status_code not in [200, 201]:
        raise HTTPException(status_code=500, detail="Failed to save user")

    return {"status": "success"}