from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "Service is running", "message": "I am alive!"}