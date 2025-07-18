from sqlalchemy.orm import Session
from .database import Chat  

def get_peer_ids_set(session: Session) -> set[int]:
    """
    Возвращает множество (set) всех peer_id из таблицы Chat.
    """
    result = session.query(Chat.peer_id).all()
    return {peer_id for (peer_id,) in result}
