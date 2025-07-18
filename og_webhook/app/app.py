from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from loguru import logger
from og_webhook.buffer import Buffer
from og_webhook.database import chat_ids, s_factory
from og_webhook.database.methods import check_user

buffer = Buffer(s_factory)


@asynccontextmanager
async def lifespan(app: FastAPI):
    buffer.start()
    yield
    buffer.flush()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def heartbrake(request: Request):
    return "ok"


@app.post("/")
async def vk_callback(request: Request):
    data = await request.json()

    if data["type"] == "confirmation":
        return PlainTextResponse(os.getenv("CONFIRMATION_TOKEN"))

    if data.get("secret") != os.getenv("SECRET_KEY"):
        return "not allowed"

    if data["type"] == "message_new":
        message = data["object"]["message"]
        if message["peer_id"] not in chat_ids:
            return PlainTextResponse("ok")

        if message.get("action"):
            with s_factory() as session:
                logger.debug(f"Действие с пользователем {message['from_id']}")

                await check_user(session, peer_id=message["from_id"])
                return PlainTextResponse("ok")

        logger.debug(f"{message['from_id']}: {message['text']}\n")
        logger.debug(f"Attachments:{message.get('attachments')}")
        buffer.append(
            {
                "peer_id": message["peer_id"],
                "from_id": message["from_id"],
                "message": message["text"],
                "date": message["date"],
            }
        )
    return PlainTextResponse("ok")
