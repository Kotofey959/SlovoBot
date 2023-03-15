from sqlalchemy import VARCHAR, Column, Integer, select

from .database import BaseModel


class User(BaseModel):
    __tablename__ = 'users'
    user_id = Column(Integer, unique=True, nullable=False, primary_key=True)
    username = Column(VARCHAR(32), unique=False, nullable=True)
    points = Column(Integer, unique=False, nullable=True, default=0)
    msg_text = Column(VARCHAR(200), unique=False, nullable=True)

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


async def get_top_users(session_maker):
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).order_by(User.points).limit(30))
            top_users = sql_res.all()
            return top_users


async def get_top_text(session_maker):
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).order_by(User.points.desc()).limit(30))
            top_users = sql_res.all()
            text = ''
            counter = 0
            for user in top_users:
                counter += 1
                if not user[0].msg_text:
                    text += f'<b>Топ-30</b>\n\n' \
                            f'{counter}) @{user[0].username} | <b>Количество баллов</b>: {user[0].points}\n' \
                            f'Здесь может быть твое сообщение\n\n'
                else:
                    text += f'<b>Топ-30</b>\n\n' \
                            f'{counter}) @{user[0].username} | <b>Количество баллов</b>: {user[0].points}\n' \
                            f'{user[0].msg_text}\n\n'
            return text
