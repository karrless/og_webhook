from collections import defaultdict
from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from loguru import logger
from og_webhook.buffer import Buffer
from og_webhook.database import s_factory
from og_webhook.database.methods import check_user, get_peer_ids_set, write_new_chat

buffer = Buffer(s_factory)

chat_ids = set()
users = defaultdict(set)
with s_factory() as session:
    chat_ids = get_peer_ids_set(session)


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
            if message.get("action"):
                if message['action']['member_id'] < 0:
                    with s_factory() as session:
                        logger.info(f"Бота добавили в {message['peer_id']}")
                        await write_new_chat(session, message['peer_id'], chat_ids)
                        session.commit()
            return PlainTextResponse("ok")

        if message.get("action"):
            with s_factory() as session:
                logger.debug(f"Действие с пользователем {message['from_id']}")
                await check_user(session, message["from_id"], users)
                
                session.commit()
            return PlainTextResponse("ok")

        logger.debug(f"{message['peer_id']}-{message['from_id']}: {message['text']}\n")

        sticker_id = None
        sticker_url = None
        attachments = message.get('attachments', [])
        for att in attachments:
            if att['type'] == 'sticker':
                sticker_data = att['sticker']
                sticker_id = sticker_data['sticker_id']
                images = sticker_data.get('images', [])
                if images:
                    sticker_url = images[-1]['url']  # Самое качественное изображение
                break
        users[message["peer_id"]].add(message["from_id"])
        buffer.append(
            {
                "peer_id": message["peer_id"],
                "from_id": message["from_id"],
                "message": message["text"],
                "date": message["date"],
                "sticker_id": sticker_id,
                "sticker_url": sticker_url
            }
        )
    return PlainTextResponse("ok")
