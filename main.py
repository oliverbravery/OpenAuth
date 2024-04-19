from fastapi import FastAPI
from routes import accounts
from database.db_manager import DBManager
from dotenv import load_dotenv
import os

load_dotenv(override=True)
DB_CONNECTION_STRING: str = os.getenv("DB_CONNECTION_STRING")
DB_NAME: str = os.getenv("DB_NAME")

app: FastAPI = FastAPI()
app.include_router(accounts.router)

db_manager: DBManager = DBManager(connection_string=DB_CONNECTION_STRING, db_name=DB_NAME)

@app.get("/")
async def root():
    return {"status": "Success", "message": "Welcome to the API!"}