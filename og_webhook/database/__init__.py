from .database import Base, connect, create, drop_all, s_factory
from .models import User, Comfort, Room, Chat, Answer, Message
from .methods import get_peer_ids_set

create()
connect()

chat_ids = {}
with s_factory() as session:
    chat_ids = get_peer_ids_set(session)
    


__all__ = [Base, connect, create, drop_all, s_factory, User, Comfort, Room, Chat, Answer, Message, chat_ids]