from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import Text, CommandStart
from sqlalchemy import select

from db import User
from db.users import get_user, create_user, get_top_users, get_top_text
from helper import get_first_random_word, get_last_letter, normalize_word, get_words_by_letter, get_random_word
from keyboards.admin import custom_kb

main_router = Router()


class GameStates(StatesGroup):
    main_menu = State()
    waiting_word = State()
    rating = State()


@main_router.message(CommandStart())
async def start_menu(message: Message, state: FSMContext, session_maker):
    if not await get_user(user_id=message.from_user.id, session_maker=session_maker):
        await create_user(user_id=message.from_user.id,
                          username=message.from_user.username,
                          session_maker=session_maker)
    await state.set_state(GameStates.main_menu)


@main_router.message(GameStates.waiting_word, Text(text='Завершить игру'))
async def end_game(message: Message, state: FSMContext):
    await state.set_state(GameStates.main_menu)
    await state.set_data({})
    await message.answer('Посмотри рейтинг игроков или начни новую игру',
                         reply_markup=custom_kb("Начать игру", "Рейтинг"))


@main_router.message(GameStates.main_menu, Text(text='Начать игру'))
async def start_game(message: Message, state: FSMContext):
    random_word = await get_first_random_word(state)
    await message.answer(f'{random_word}. Придумай слово на {get_last_letter(random_word).upper()}.',
                         reply_markup=custom_kb("Завершить игру"))
    await state.set_state(GameStates.waiting_word)
    await state.update_data(previous_word=random_word)
    await state.update_data(used_words=[random_word.lower()])


@main_router.message(GameStates.waiting_word)
async def game(message: Message, state: FSMContext, session_maker):
    text = normalize_word(message.text)
    data = await state.get_data()
    previous_word = data.get('previous_word')
    used_words = data.get('used_words')
    if not text.isalpha():
        await message.answer('Слово должно содержать только буквы')
        return
    if text[0] != get_last_letter(previous_word):
        await message.answer(f'Слово должно начинаться на букву {get_last_letter(previous_word).upper()}')
        return
    if text in used_words:
        await message.answer('Данное слово уже использовалось. Попробуй другое')
        return
    if text not in get_words_by_letter(text[0]):
        await message.answer('Я знаю очень много слов, но с таким не встречался, попробуй другое.')
        return
    random_word = await get_random_word(text, state=state)
    await message.answer(f'{random_word.capitalize()}. Придумай слово на {get_last_letter(random_word).upper()}',
                         reply_markup=custom_kb("Завершить игру"))
    await state.update_data(previous_word=random_word)
    used_words.append(text)
    used_words.append(random_word)
    await state.update_data(used_words=used_words)
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).filter_by(user_id=message.from_user.id))
            user: User = sql_res.scalar()
            user.points += 1


@main_router.message(GameStates.main_menu, Text(text='Рейтинг'))
async def rating(message: Message, state: FSMContext, session_maker):
    await state.set_state(GameStates.rating)
    text = await get_top_text(session_maker)
    await message.answer(text, reply_markup=custom_kb('Изменить сообщение', 'Главное меню'))


# @main_router.message(GameStates.rating, Text(text='Изменить сообщение'))
# async def change_msg(message: Message, state: FSMContext, session_maker):
