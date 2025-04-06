import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware import Middleware

from api.rsecrets import secrets


app = FastAPI()


app = FastAPI()


@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


app.include_router(secrets)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="127.0.0.1", port=8080)
