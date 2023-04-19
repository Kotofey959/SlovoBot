from typing import List

from aiogram.fsm.context import FSMContext

from db.users import get_admins_list_text


def normalize_word(word: str) -> str:
    """
    Приводим слово к общему виду

    """
    return word.strip().lower()


def get_last_letter(word: str) -> str:
    """
    Получение последней буквы слова

    """
    if word[-1] in 'ъьы':
        return word[-2]
    else:
        return word[-1]


async def check_word_used(word: str, state: FSMContext) -> bool:
    """
    Проверяем входит ли слово в список уже использованных

    """
    data = await state.get_data()
    word = normalize_word(word)
    return word in data.get("used_words")


async def get_admin_username(text: str, session_maker):
    """
    Проверяем является ли пользователь с переданным юзернеймом администратором

    :param session_maker:
    :param text: юзернейм
    """
    admins_list = await get_admins_list_text(session_maker)
    if text not in admins_list:
        return None
    return text


def create_ref_link(user_id: int) -> str:
    """
    Создаем реферальную ссылку с переданным id

    """
    return f"https://t.me/SlovogonBot?start={user_id}"


def get_ref_id(link: str) -> int or None:
    """
    Достаем из переданной ссылки id рефера

    """
    link_split = link.split()
    if len(link_split) == 2 and link_split[1].isdigit():
        return int(link_split[1])
    return None


def new_words_to_list(new_words: str) -> List[str]:
    """
    Преобразуем переданные слова в список слов

    :param new_words: слова через запятую
    :return: список слов
    """
    return [normalize_word(word) for word in new_words.split(",")]
