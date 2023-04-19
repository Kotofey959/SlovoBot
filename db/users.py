from sqlalchemy import VARCHAR, Column, Integer, select, Boolean

from .database import BaseModel


class User(BaseModel):
    __tablename__ = 'users'
    user_id = Column(Integer, unique=True, nullable=False, primary_key=True)
    username = Column(VARCHAR(32), unique=False, nullable=True)
    points = Column(Integer, unique=False, nullable=True, default=0)
    msg_text = Column(VARCHAR(200), unique=False, nullable=True)
    status = Column(VARCHAR(6), unique=False, default='user')
    in_top = Column(Boolean, unique=False, default=False)

    def __str__(self):
        return f'<User:{self.user_id}>'


async def create_user(user_id: int, username: str, session_maker):
    """
    Создание пользователя в БД

    """
    async with session_maker() as session:
        async with session.begin():
            user = User(
                user_id=user_id,
                username=username
            )

            session.add(user)


async def get_user(user_id: int, session_maker) -> User:
    """
    Получение пользователя по id

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            return user


async def get_user_by_name(username: str, session_maker) -> User:
    """
    Получение пользователя по username

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.username == username))
            user: User = sql_res.scalar()
            return user


async def get_top_text(session_maker) -> str:
    """
    Формирование текста Топ 10 пользователей с их сообщениями

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).order_by(User.points.desc()).limit(10))
            top_users = sql_res.all()
            text = '<b>Топ-10</b>\n\n'
            counter = 0
            for user in top_users:
                counter += 1
                if not user[0].msg_text:
                    text += f'{counter}) @{user[0].username} | <b>Количество баллов</b>: {user[0].points}\n' \
                            f'Здесь может быть твое сообщение\n\n'

                else:
                    text += f'{counter}) @{user[0].username} | <b>Количество баллов</b>: {user[0].points}\n' \
                            f'{user[0].msg_text}\n\n'

            return text


async def change_user_message(user_id: int, msg_text: str, session_maker):
    """
    Изменение сообщения пользователя в БД

    :param user_id:
    :param msg_text: новый текст
    :param session_maker:
    :return:
    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            user.msg_text = msg_text


async def get_top_id_list(session_maker):
    """
    Получение списка id топ 10 пользователей по баллам

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).order_by(User.points.desc()).limit(10))
            top_users = sql_res.all()
            id_list = []
            for user in top_users:
                id_list.append(user[0].user_id)
            return id_list


async def get_users_count(session_maker) -> int:
    """
    Получение общего количества пользователей

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User))
            return len(sql_res.all())


async def check_admin(user_id: int, session_maker):
    """
    Проверяем является ли пользователь администратором

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            return bool(user.status == 'admin')


async def get_admins_list_text(session_maker):
    """
    Получение списка юзернеймов администраторов

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.status == 'admin'))
            admin_list = sql_res.all()
            return [admin[0].username for admin in admin_list]


async def del_admin_from_db(username: str, session_maker):
    """
        Установление пользователю статуса User

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.username == username))
            user: User = sql_res.scalar()
            user.status = 'user'


async def add_admin_to_db(username: str, session_maker):
    """
    Установление пользователю статуса Admin

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.username == username))
            user: User = sql_res.scalar()
            user.status = 'admin'


async def check_user_in_top(user_id: int, session_maker):
    """
        Получение параметра 'in_top' у пользователя

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            return bool(user.in_top)


async def change_top_user(user_id: int, session_maker, in_top: bool):
    """
    Изменение параметра 'in_top' у пользователя

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            user.in_top = in_top


async def get_all_users_id(session_maker):
    """
    Получения списка id всех пользователей

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User))
            all_users = sql_res.all()
            id_list = []
            for user in all_users:
                id_list.append(user[0].user_id)
            return id_list


async def change_points(user_id: int, session_maker, points=1):
    """
    Изменение баллов пользователя

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            user.points += points


async def get_user_points(user_id: int, session_maker):
    """
    Получаем баллы пользователя из БД

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            points = user.points
            return points


async def check_ban(user_id: int, session_maker):
    """
    Проверяем забанен ли пользователь

    """
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            return bool(user.status == 'ban')


async def ban_user(username: str, session_maker):
    """
    Баним пользователя по username

    """
    async with session_maker() as session:
        async with session.begin():
            user_data = username.strip()
            sql_res = await session.execute(select(User).where(User.username == user_data))
            user: User = sql_res.scalar()
            user.status = 'ban'
