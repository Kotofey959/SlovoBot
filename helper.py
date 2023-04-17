import json
import random
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


def get_words_by_letter(letter: str) -> list[str]:
    """
    Получаем список слов на заданную букву

    """
    with open("words.json", "r", encoding='Windows-1251') as f:
        words = json.load(f)
        return words.get(letter)


async def check_word_used(word: str, state: FSMContext) -> bool:
    """
    Проверяем входит ли слово в список уже использованных

    """
    data = await state.get_data()
    word = normalize_word(word)
    return word in data.get("used_words")


async def check_word_in_dict(word: str) -> bool:
    """
    Проверяем есть ли данное слово в словаре

    """
    with open("words.json", "r", encoding='Windows-1251') as f:
        words = json.load(f)
        word = normalize_word(word)
        return word in words.get(word[0])


async def get_random_word(word: str, state: FSMContext) -> str:
    """
    Получаем рандомное слово из словаря на последнюю букву переданного слова

    """
    with open("words.json", "r", encoding='Windows-1251') as f:
        words = json.load(f)
        data = await state.get_data()
        used_words = data.get("used_words")
        normal_word = normalize_word(word)
        words_list = words.get(get_last_letter(normal_word))
        for word1 in used_words:
            if word1[0] == get_last_letter(normal_word):
                words_list.remove(word1)
        random_word = random.choice(words_list)
        await state.update_data(previous_word=random_word)
        return random_word


async def get_first_random_word(state: FSMContext) -> str:
    """
    Для начала игры получаем рандомное слово из словаря

    """
    with open("words.json", "r", encoding='Windows-1251') as f:
        words = json.load(f)
        random_letter = random.choice(list(words.keys()))
        random_word = random.choice(list(words.get(random_letter)))
        await state.update_data(previous_word=random_word)
        return random_word.capitalize()


async def get_admin_username(text: str, session_maker):
    """
    Проверяем является ли пользователь с переданным юзернеймом администратором

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


def add_new_words(lst_words: List[str]) -> None:
    """
    Добавляем переданный список слов в словарь

    """
    with open("words.json", 'r', encoding='Windows-1251') as file:
        words = json.load(file)
        for word in lst_words:
            words.get(word[0]).append(word)
        with open("words.json", "w", encoding='Windows-1251') as f:
            json.dump(words, f, indent=4, ensure_ascii=False)


def check_words_in_dict(lst_words: List[str]) -> List[str, None]:
    """
    Проверяем есть ли слова из переданного списка в словаре

    """
    with open("words.json", 'r', encoding='Windows-1251') as file:
        words = json.load(file)
        invalid_words = []
        for word in lst_words:
            if word in words.get(word[0]):
                invalid_words.append(word)
        return invalid_words


