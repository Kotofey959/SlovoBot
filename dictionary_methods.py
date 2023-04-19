import json
import random
from typing import List

from aiogram.fsm.context import FSMContext

from helper import normalize_word, get_last_letter


def get_words_by_letter(letter: str, file_name="words.json") -> List[str]:
    """
    Получаем список слов на заданную букву

    """
    with open(file_name, "r", encoding='Windows-1251') as f:
        words = json.load(f)
        return words.get(letter)


async def check_word_in_dict(word: str, file_name="words.json") -> bool:
    """
    Проверяем есть ли данное слово в словаре

    """
    with open(file_name, "r", encoding='Windows-1251') as f:
        words = json.load(f)
        word = normalize_word(word)
        return word in words.get(word[0])


async def get_random_word(word: str, state: FSMContext, file_name="words.json") -> str:
    """
    Получаем рандомное слово из словаря на последнюю букву переданного слова

    """
    with open(file_name, "r", encoding='Windows-1251') as f:
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


async def get_first_random_word(state: FSMContext, file_name="words.json") -> str:
    """
    Для начала игры получаем рандомное слово из словаря

    """
    with open(file_name, "r", encoding='Windows-1251') as f:
        words = json.load(f)
        random_letter = random.choice(list(words.keys()))
        random_word = random.choice(list(words.get(random_letter)))
        await state.update_data(previous_word=random_word)
        return random_word.capitalize()


def add_new_words(lst_words: List[str], file_name="words.json") -> None:
    """
    Добавляем переданный список слов в словарь

    """
    with open(file_name, 'r', encoding='Windows-1251') as file:
        words = json.load(file)
        for word in lst_words:
            words.get(word[0]).append(word)
        with open("words.json", "w", encoding='Windows-1251') as f:
            json.dump(words, f, indent=4, ensure_ascii=False)


def check_words_in_dict(lst_words: List[str], file_name="words.json") -> List[str]:
    """
    Проверяем есть ли слова из переданного списка в словаре

    """
    with open(file_name, 'r', encoding='Windows-1251') as file:
        words = json.load(file)
        invalid_words = []
        for word in lst_words:
            if word in words.get(word[0]):
                invalid_words.append(word)
        return invalid_words


def game_validator(text: str, previous_word: str, used_words: List[str]):
    """
    Проверяем сообщения от пользователя на корректность

    :param text: сообщение от пользователя
    :param previous_word: предыдущее слово
    :param used_words: список использованных слов
    :return:
    """
    if not text.isalpha():
        return "Слово должно содержать только буквы"
    if text[0] != get_last_letter(previous_word):
        return f"Слово должно начинаться на букву {get_last_letter(previous_word).upper()}"
    if text in used_words:
        return "Данное слово уже использовалось. Попробуй другое"
    if text not in get_words_by_letter(text[0]):
        return "Я знаю очень много слов, но с таким не встречался, попробуй другое."
    return
