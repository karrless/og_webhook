from dotenv import load_dotenv
import os
from loguru import logger

load_dotenv()
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO",
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
)


def connect_db():
    import og_webhook.database as db

    db.create()
    db.connect()


def app_start():
    import uvicorn
    connect_db()
    uvicorn.run(
        "og_bots.app:app", host=os.environ("HOST"), port=os.environ("PORT"), reload=True
    )

