from fastapi import FastAPI
from database.db_manager import DBManager
from dotenv import load_dotenv
import os

load_dotenv(override=True)
DB_CONNECTION_STRING: str = os.getenv("DB_CONNECTION_STRING")
DB_NAME: str = os.getenv("DB_NAME")

db_manager: DBManager = DBManager(connection_string=DB_CONNECTION_STRING, db_name=DB_NAME)

app: FastAPI = FastAPI()

from routes.account import account_router
app.include_router(account_router.router)

@app.get("/")
async def root():
    return {"status": "Success", "message": "Welcome to the API!"}