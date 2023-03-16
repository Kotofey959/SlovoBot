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


async def create_user(user_id, username, session_maker):
    async with session_maker() as session:
        async with session.begin():
            user = User(
                user_id=user_id,
                username=username
            )

            session.add(user)


async def get_user(user_id, session_maker) -> User:
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            return user


async def get_user_by_name(username, session_maker) -> User:
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.username == username))
            user: User = sql_res.scalar()
            return user


async def get_top_users(session_maker):
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).order_by(User.points).limit(10))
            top_users = sql_res.all()
            return top_users


async def get_top_text(session_maker):
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


async def change_user_message(user_id, msg_text, session_maker):
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            user.msg_text = msg_text


async def get_top_id_list(session_maker):
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).order_by(User.points.desc()).limit(10))
            top_users = sql_res.all()
            id_list = []
            for user in top_users:
                id_list.append(user[0].user_id)
            return id_list


async def get_users_count(session_maker):
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User))
            return len(sql_res.all())


async def check_admin(user_id, session_maker):
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            return bool(user.status == 'admin')


async def get_admins_list_text(session_maker):
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.status == 'admin'))
            admin_list = sql_res.all()
            return [f'{admin[0].username}' for admin in admin_list]


async def del_admin_from_db(username, session_maker):
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.username == username))
            user: User = sql_res.scalar()
            user.status = 'user'


async def add_admin_to_db(username, session_maker):
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.username == username))
            user: User = sql_res.scalar()
            user.status = 'admin'


async def check_user_in_top(user_id, session_maker):
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            return bool(user.in_top)


async def change_top_user(user_id, session_maker, in_top):
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            user: User = sql_res.scalar()
            user.in_top = in_top
