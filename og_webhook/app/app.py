import os
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from loguru import logger
from og_webhook.database import chat_ids
app = FastAPI()

@app.get("/")
async def heartbrake(request: Request):
    return "ok"


@app.post("/")
async def vk_callback(request: Request):
    data = await request.json()

    if data["type"] == "confirmation":
        return PlainTextResponse(os.getenv("CONFIRMATION_TOKEN"))

    if data.get("secret") != os.getenv('SECRET_KEY'):
        return "not allowed"

    if data["type"] == "message_new":
        message = data["object"]["message"]
        if message['peer_id'] not in chat_ids:
            return PlainTextResponse("ok")
        
        logger.info(f"{message['from_id']}: {message['text']}\n")

    return PlainTextResponse("ok")
