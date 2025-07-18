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


async def check_user(session: Session, from_id, peer_id, users:dict[int, set]):
    if users.get(peer_id):
        if from_id in users['peer_id']:
            return
    user = await api.users.get(user_ids=[from_id], fields=['screen_name'])[0]
    try:
        session.add(
            User(
                peer_id=from_id,
                screen_name=user.screen_name,
                name=user.first_name,
                surname=user.last_name,
            )
        )
    except IntegrityError:
        session.rollback()
    users['peer_id'].add(from_id)


# async def write_users(session: Session, peer_id: int):
#     response = await api.messages.get_conversation_members(peer_id=peer_id)

#     users = []
#     for profile in response.profiles:
#         users.append({
#             "peer_id": profile.id,
#             "screen_name": profile.screen_name,
#             "name": profile.first_name,
#             "surname": profile.last_name,
#         })

#     stmt = insert(User).values(users)
#     stmt = stmt.on_conflict_do_update(
#         index_elements=["peer_id"],  # по какому полю определять конфликт (обычно PRIMARY KEY)
#         set_={
#             "screen_name": stmt.excluded.screen_name,
#             "name": stmt.excluded.name,
#             "surname": stmt.excluded.surname
#         }
#     )

#     session.execute(stmt)
#     session.commit()

async def write_new_chat(session: Session, peer_id, chat_ids):
    conv = await api.messages.get_conversations_by_id(peer_ids=[peer_id])
    chat = Chat(
        peer_id=peer_id,
        faculty=conv.items[0].chat_settings.title,
        color='#4682B4'
    )
    session.add(chat)
    session.flush()
    chat_ids.add(peer_id)
    