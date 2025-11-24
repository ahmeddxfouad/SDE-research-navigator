import os
import requests
import jwt
import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

app = FastAPI()

USER_DATA_URL = os.getenv("USER_DATA_URL", "http://user-data-service:80")
SECRET_KEY = "my_super_secret_key"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginPayload(BaseModel):
    email: EmailStr
    password: str

@app.post("/login")
def login(data: LoginPayload):
    try:
        user_resp = requests.get(f"{USER_DATA_URL}/users/{data.email}")
        if user_resp.status_code == 404:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Data Service Unavailable")

    user_data = user_resp.json()
    stored_hash = user_data.get("password_hash")

    if not pwd_context.verify(data.password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

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