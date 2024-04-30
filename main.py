from fastapi import FastAPI

app: FastAPI = FastAPI()

from routes import account_router
app.include_router(account_router.router)

from routes import authentication_router
app.include_router(authentication_router.router)

from routes import developer_router
app.include_router(developer_router.router)

from routes import well_known
app.include_router(well_known.router)

from routes import client_router
app.include_router(client_router.router)

@app.get("/")
async def root():
    return {"status": "Success", "message": "Welcome to the API!"}