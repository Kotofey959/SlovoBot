from typing import Text

from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def custom_kb(*kwargs: Text):
    builder = ReplyKeyboardBuilder()
    for value in kwargs:
        builder.add(types.KeyboardButton(text=value))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def del_admin_kb(admin_list: list[str]):
    builder = ReplyKeyboardBuilder()
    for value in admin_list:
        builder.add(types.KeyboardButton(text=value))
    builder.add(types.KeyboardButton(text='Админ панель'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)