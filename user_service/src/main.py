from fastapi import FastAPI

app = FastAPI(title="User Service")

@app.get("/")
async def root():
    return {"message": "User Service is running"}