from dotenv import load_dotenv
import os
from loguru import logger

load_dotenv()
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    level=os.getenv('LOG_LEVEL'),
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
)


def app_start():
    import uvicorn
    uvicorn.run(
        "og_webhook.app:app", host=os.getenv("HOST"), port=int(os.getenv("PORT")), reload=True
    )

