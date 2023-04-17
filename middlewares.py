from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject

from db.users import check_ban


class BanMiddleWare(BaseMiddleware):
    """
    На каждом сообщении проверяем не забанен ли пользователь

    """
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if not await check_ban(data['event_from_user'].id, session_maker=data.get("session_maker")):
            return await handler(event, data)