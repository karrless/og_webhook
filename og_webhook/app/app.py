import os
from fastapi import FastAPI, Request
from loguru import logger
app = FastAPI()


@app.post("/")
async def vk_callback(request: Request):
    data = await request.json()

    if data["type"] == "confirmation":
        return os.environ("CONFIRMATION_TOKEN")

    if data.get("secret") != os.environ('SECRET_KEY'):
        return "not allowed"

    if data["type"] == "message_new":
        message = data["object"]["message"]
        logger.info(f"{message['from_id']}: {message['text']}\n")

    return "ok"
