from fastapi import FastAPI

from api.structlogger import logger

app = FastAPI()

@app.get("/")
def read_root() -> dict[str, str]:
    logger.info("GET /")
    return {"message": "Hello! This is the root endpoint."}
