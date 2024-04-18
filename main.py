from fastapi import FastAPI
from routers import *

app: FastAPI = FastAPI()

@app.get("/")
async def root():
    return {"status": "Success", "message": "Welcome to the API!"}