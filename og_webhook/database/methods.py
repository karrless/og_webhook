import random
from sqlalchemy.orm import Session

from og_webhook.api import api
from .models import Chat, User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert

def get_peer_ids_set(session: Session) -> set[int]:
    """
    Возвращает множество (set) всех peer_id из таблицы Chat.
    """
    result = session.query(Chat.peer_id).all()
    return {peer_id for (peer_id,) in result}


async def check_user(session: Session, from_id, peer_id, users:dict[int, set]):
    if users.get(peer_id):
        if from_id in users[peer_id]:
            return
        
    user = (await api.users.get(user_ids=[from_id], fields=['screen_name']))[0]
    stmt = insert(User).values(
    peer_id=from_id,
    screen_name=user.screen_name,
    name=user.first_name,
    surname=user.last_name,
    ).on_conflict_do_nothing(
        index_elements=["peer_id"]  # поле, по которому проверяется конфликт
    )

    session.execute(stmt)

    users['peer_id'].add(from_id)


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
    
async def add_new_chat(peer_id, chat_ids):
    chat_ids.add(peer_id)
    text = ('Привет! Я бот "Окей, Горный"!\n'
            'Назначь меня адмиинистратором и после этого введи команду /add [название направления], например:\n'
            '/add НПМС')
    await api.messages.send(peer_id=peer_id, random_id=random.randint(1, peer_id), message=text)
