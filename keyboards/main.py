from typing import Text

from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def custom_kb(*kwargs: Text):
    """
    Создание клавиатур с произвольным количеством кнопок

    :param kwargs: строки с текстом для клавиатуры

    """
    builder = ReplyKeyboardBuilder()
    for value in kwargs:
        builder.add(types.KeyboardButton(text=value))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def del_admin_kb(admin_list: list[str]):
    """
    Создание клавиатуры со списком администраторов

    :param admin_list: список юзернеймов администраторов

    """
    builder = ReplyKeyboardBuilder()
    for value in admin_list:
        builder.add(types.KeyboardButton(text=value))
    builder.add(types.KeyboardButton(text='Админ панель'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)
