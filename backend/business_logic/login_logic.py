import os
import requests
import jwt
import datetime
import bcrypt
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI()

USER_DATA_URL = os.getenv("USER_DATA_URL", "http://user-data-service:80")
SECRET_KEY = os.getenv("JWT_SECRET", "THIS_IS_A_FALLBACK")

class LoginPayload(BaseModel):
    email: EmailStr
    password: str

@app.post("/login")
def login(data: LoginPayload):
    # Fetch User Data
    try:
        user_resp = requests.get(f"{USER_DATA_URL}/users/{data.email}")
        if user_resp.status_code == 404:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Data Service Unavailable")

    user_data = user_resp.json()
    stored_hash = user_data.get("password_hash")

    if not stored_hash:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Convert both to bytes for bcrypt
    input_bytes = data.password.encode('utf-8')
    stored_hash_bytes = stored_hash.encode('utf-8')

    if not bcrypt.checkpw(input_bytes, stored_hash_bytes):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate Token
    token_payload = {
        "sub": user_data["email"],
        "name": user_data.get("full_name"),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    
    token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

    return {
        "access_token": token, 
        "token_type": "bearer",
        "user_name": user_data.get("full_name")
    }