import json
import random

from aiogram.fsm.context import FSMContext


def normalize_word(word: str) -> str:
    return word.strip().lower()


def get_last_letter(word: str) -> str:
    if word[-1] in 'ъьы':
        return word[-2]
    else:
        return word[-1]


def get_words_by_letter(letter: str) -> list[str]:
    with open("words.json", "r") as f:
        words = json.load(f)
        return words.get(letter)


async def check_word_used(word, state: FSMContext) -> bool:
    data = await state.get_data()
    word = normalize_word(word)
    return word in data.get("used_words")


async def check_word_in_dict(word) -> bool:
    with open("words.json", "r") as f:
        words = json.load(f)
        word = normalize_word(word)
        return word in words.get(word[0])


async def get_random_word(word: str, state: FSMContext) -> str:
    with open("words.json", "r") as f:
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
    with open("words.json", "r") as f:
        words = json.load(f)
        random_letter = random.choice(list(words.keys()))
        random_word = random.choice(list(words.get(random_letter)))
        await state.update_data(previous_word=random_word)
        return random_word.capitalize()



