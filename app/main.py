import uvicorn

from fastapi import FastAPI

from api.secrets import secrets


app = FastAPI()

app.include_router(secrets)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080)
