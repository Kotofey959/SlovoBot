from sqlalchemy import VARCHAR, Column, Integer

from .database import BaseModel


class AdminMsg(BaseModel):
    __tablename__ = 'AdminMsg'
    num_msg = Column(VARCHAR(4), unique=True, nullable=False, primary_key=True)
    msg_text = Column(VARCHAR(500), unique=False, nullable=True)
