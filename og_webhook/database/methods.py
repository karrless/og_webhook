from sqlalchemy.orm import Session

from og_webhook.api import api
from .models import Chat, User
from sqlalchemy.exc import IntegrityError


def get_peer_ids_set(session: Session) -> set[int]:
    """
    Возвращает множество (set) всех peer_id из таблицы Chat.
    """
    result = session.query(Chat.peer_id).all()
    return {peer_id for (peer_id,) in result}


async def check_user(session: Session, peer_id):
    user = api.users.get(user_ids=[peer_id], fields=['screen_name'])[0]
    try:
        session.add(
            User(
                peer_id=peer_id,
                screen_name=user.screen_name,
                name=user.first_name,
                surname=user.last_name,
            )
        )
        session.commit()
    except IntegrityError:
        session.rollback()
