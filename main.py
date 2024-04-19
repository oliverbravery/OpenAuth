from fastapi import FastAPI
from routes import accounts

app: FastAPI = FastAPI()
app.include_router(accounts.router)

@app.get("/")
async def root():
    return {"status": "Success", "message": "Welcome to the API!"}