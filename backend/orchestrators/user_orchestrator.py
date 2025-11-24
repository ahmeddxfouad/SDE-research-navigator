import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI(title="User Orchestrator")

# Service URLs from Docker Compose
REGISTER_URL = os.getenv("REGISTER_URL", "http://register-logic:80")
LOGIN_URL = os.getenv("LOGIN_URL", "http://login-logic:80")

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

@app.get("/")
def health_check():
    return {"status": "User Orchestrator Online"}

@app.post("/register")
def register_user(user_data: UserRegisterRequest):
    try:
        response = requests.post(f"{REGISTER_URL}/register", json=user_data.dict())

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail=response.json().get("detail", "Registration failed")
            )
            
        return response.json()

    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Registration Service Unavailable")

@app.post("/login")
def login_user(credentials: UserLoginRequest):
    try:
        response = requests.post(f"{LOGIN_URL}/login", json=credentials.dict())

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail=response.json().get("detail", "Login failed")
            )

        return response.json()

    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Login Service Unavailable")