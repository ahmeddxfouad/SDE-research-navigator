import os
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import List

app = FastAPI()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo-db:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client.university_project_db

class UserDocument(BaseModel):
    email: EmailStr
    full_name: str
    password_hash: str
    favorites: List[dict] = []

@app.get("/users/{email}")
async def get_user_by_email(email: str):
    user = await db.users.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])
        return user
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/users", status_code=201)
async def create_user(user: UserDocument):
    user_dict = user.dict()
    result = await db.users.insert_one(user_dict)
    return {"id": str(result.inserted_id)}