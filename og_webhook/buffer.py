import asyncio
import os
from threading import Lock
from loguru import logger
from sqlalchemy.dialects.postgresql import insert
from og_webhook.database.models import Message


class Buffer:
    def __init__(self, session_factory):
        self.FLUSH_SIZE = int(os.getenv("FLUSH_SIZE"))
        self.FLUSH_INTERVAL = int(os.getenv("FLUSH_INTERVAL"))
        
        self.data: list[dict] = []
        self.seen: set[tuple[int, int]] = set()
        self.lock = Lock()
        self.s_factory = session_factory
    
    def append(self, data: dict):
        key = (data["peer_id"], data["conversation_message_id"])
        with self.lock:
            if key in self.seen:
                return
            self.seen.add(key)
            self.data.append(data)
            
            if len(self.data) >= self.FLUSH_SIZE:
                self._flush_locked()

    def flush(self):
        with self.lock:
            self._flush_locked()
    
    def _flush_locked(self):
        if not self.data:
            return
        
        batch = self.data.copy()
        self.data.clear()
        self.seen.clear()

        with self.s_factory() as session:
            stmt = insert(Message).values(batch)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["peer_id", "conversation_message_id"]
            )
            session.execute(stmt)
            session.commit()
        
        logger.debug(f"Попытка вставки {len(batch)} сообщений (дубликаты будут проигнорированы)")


            
    async def scheduler(self):
        while True:
            await asyncio.sleep(self.FLUSH_INTERVAL)
            self.flush()
            
    def start(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.scheduler())

