from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine

from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

server = SSHTunnelForwarder(
    ('85.142.103.65', 10000),
    ssh_username='remoteadm',
    ssh_password=os.getenv('SSH_PASS'),  # или private_key='path_to_key'
    remote_bind_address=('127.0.0.1', 5432),
    local_bind_address=('127.0.0.1', 6543)  # локальный порт
)

server.start()

engine = create_engine(os.getenv('DB_URI'))

s_factory = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


def connect():
    """
    Подключение к базе данных
    :return:
    """
    engine.connect()


def create():
    """
    Создание таблиц
    :return:
    """
    Base.metadata.create_all(engine)


def drop_all(tables: list = None):
    """
    Удаление таблицы
    :param tables: список таблиц
    :return:
    """
    if tables:
        Base.metadata.drop_all(engine, tables=tables)
    else:
        Base.metadata.drop_all(engine)
