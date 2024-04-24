from fastapi import FastAPI

app: FastAPI = FastAPI()

from routes.account import account_router
app.include_router(account_router.router)

from routes.authentication import authentication_router
app.include_router(authentication_router.router)

from routes.developer import developer_router
app.include_router(developer_router.router)

@app.get("/")
async def root():
    return {"status": "Success", "message": "Welcome to the API!"}