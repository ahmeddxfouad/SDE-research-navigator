import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

app = FastAPI()

USER_DATA_URL = os.getenv("USER_DATA_URL", "http://user-data-service:80")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterPayload(BaseModel):
    email: EmailStr
    password: str
    full_name: str

@app.post("/register")
def register(data: RegisterPayload):
    try:
        check_resp = requests.get(f"{USER_DATA_URL}/users/{data.email}")
        if check_resp.status_code == 200:
            raise HTTPException(status_code=400, detail="Email already registered")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Data Service Unavailable")

    hashed_password = pwd_context.hash(data.password)

    new_user = {
        "email": data.email,
        "full_name": data.full_name,
        "password_hash": hashed_password,
        "favorites": []
    }

    save_resp = requests.post(f"{USER_DATA_URL}/users", json=new_user)

    if save_resp.status_code not in [200, 201]:
        raise HTTPException(status_code=500, detail="Failed to save user")

    return {"status": "success"}