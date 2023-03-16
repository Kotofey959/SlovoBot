from sqlalchemy import VARCHAR, Column, Integer, select

from .database import BaseModel


class AdminMsg(BaseModel):
    __tablename__ = 'AdminMsg'
    num_msg = Column(VARCHAR(20), unique=True, nullable=False, primary_key=True)
    msg_text = Column(VARCHAR(1200), unique=False, nullable=True)


async def change_msg(num_msg, msg_text, session_maker):
    async with session_maker() as session:
        async with session.begin():
            sqlres = await session.execute(select(AdminMsg).where(AdminMsg.num_msg == num_msg))
            msg = sqlres.scalar()
            msg.msg_text = msg_text


async def get_msg_text(num_msg, session_maker):
    async with session_maker() as session:
        async with session.begin():
            sqlres = await session.execute(select(AdminMsg).where(AdminMsg.num_msg == num_msg))
            msg = sqlres.scalar()
            msg_text = msg.msg_text
            return msg_text


async def get_admin_text(session_maker):
    async with session_maker() as session:
        async with session.begin():
            sqlres = await session.execute(select(AdminMsg))
            msg_list = sqlres.all()
            admin_text = ''
            for text in msg_list:
                if text[0].msg_text:
                    admin_text += f"{text[0].msg_text}\n\n"
            return admin_text

