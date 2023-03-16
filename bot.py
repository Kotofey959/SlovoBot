import asyncio
import logging
import os
from environs import Env

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import URL
from db import create_async_engine, get_session_maker, proceed_schemas, BaseModel
from handlers import main as m, admin

logger = logging.getLogger(__name__)
env = Env()
env.read_env()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s '
               u'[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    bot: Bot = Bot(token=env('BOT_TOKEN'), parse_mode='HTML')
    dp: Dispatcher = Dispatcher(storage=MemoryStorage())

    postgres_url = URL.create(
        'postgresql+asyncpg',
        username='postgres',
        password='Lol4ik594770146',
        host='localhost',
        port=5432,
        database='SlovoBot'

    )

    async_engine = create_async_engine(postgres_url)
    session_maker = get_session_maker(async_engine)
    await proceed_schemas(async_engine, BaseModel.metadata)

    dp.include_router(m.main_router)
    dp.include_router(admin.admin_router)
    await dp.start_polling(bot, session_maker=session_maker)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped!')