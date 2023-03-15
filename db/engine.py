from sqlalchemy import MetaData
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine as cr_async_engine, AsyncSession,\
    AsyncEngine, async_sessionmaker


def create_async_engine(url: URL | str) -> AsyncEngine:
    return cr_async_engine(url=url, pool_pre_ping=True, echo=True)


async def proceed_schemas(engine: AsyncEngine, metadata: MetaData) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


def get_session_maker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(bind=engine, class_=AsyncSession)