import asyncio
import os
from threading import Lock
from loguru import logger
from og_webhook.database.models import Message


class Buffer:
    def __init__(self, session_factory):
        self.FLUSH_SIZE = int(os.getenv("FLUSH_SIZE"))
        self.FLUSH_INTERVAL = int(os.getenv("FLUSH_INTERVAL"))
        
        self.data: list[dict] = []
        self.lock = Lock()
        self.s_factory = session_factory
    
    def append(self, data: dict):
        self.data.append(data)
        if len(self.data) >= self.FLUSH_SIZE:
            self.flush()

    def flush(self):
        with self.lock:
            if not self.data:
                return
        
        _copy = self.data.copy()
        self.data.clear()
        
        with self.s_factory() as session:
            session.bulk_insert_mappings(Message, _copy)
            session.commit()
                
        logger.debug(f"Отправлено {len(_copy)} сообщений")

            
    async def scheduler(self):
        while True:
            await asyncio.sleep(self.FLUSH_INTERVAL)
            self.flush()
            
    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.scheduler())

