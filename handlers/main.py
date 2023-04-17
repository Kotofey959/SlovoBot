from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import Text, CommandStart
from sqlalchemy import select

from db import User
from db.admin_msg import get_admin_text, get_text_about_project
from db.users import get_user, create_user, get_top_text, get_top_id_list, change_user_message, \
    check_user_in_top, change_top_user, add_ref_to_user, get_user_points
from helper import get_first_random_word, get_last_letter, normalize_word, get_words_by_letter, get_random_word, \
    create_ref_link, get_ref_id
from keyboards.main import custom_kb

main_router = Router()


class GameStates(StatesGroup):
    main_menu = State()
    waiting_word = State()
    rating = State()
    change_msg = State()
    check_msg = State()


@main_router.message(CommandStart())
async def start_menu(message: Message, state: FSMContext, session_maker):
    """
    Обработка команды старт

    """
    if not await get_user(user_id=message.from_user.id, session_maker=session_maker):
        await create_user(user_id=message.from_user.id,
                          username=message.from_user.username,
                          session_maker=session_maker)
        ref_id = get_ref_id(message.text)
        if ref_id and await get_user(user_id=ref_id, session_maker=session_maker):
            await add_ref_to_user(user_id=ref_id, session_maker=session_maker)
    await state.set_state(GameStates.main_menu)
    await state.set_data({})
    await message.answer('Посмотри рейтинг игроков или начни новую игру',
                         reply_markup=custom_kb("Начать игру", "Рейтинг",
                                                "Пригласи друга и получи 100 баллов", "О проекте"))


@main_router.message(Text(text=['Завершить игру', 'Главное меню']))
async def end_game(message: Message, state: FSMContext):
    """
    Перевод в главное меню при нажатии кнопок Завершить игру и Главное меню

    """
    await state.set_state(GameStates.main_menu)
    await state.set_data({})
    await message.answer('Посмотри рейтинг игроков или начни новую игру',
                         reply_markup=custom_kb("Начать игру", "Рейтинг",
                                                "Пригласи друга и получи 100 баллов", "О проекте"))


@main_router.message(GameStates.main_menu, Text(text='Пригласи друга и получи 100 баллов'))
async def game_rating(message: Message):
    """
    Отправляем сообщение с реферальной ссылкой пользователя

    """
    ref_link = create_ref_link(message.from_user.id)
    await message.answer(f"Отправьте ссылку на бота другу. Когда он перейдет по ней в бота, вы получите 100 баллов.")
    await message.answer(ref_link, reply_markup=custom_kb("Главное меню"))


@main_router.message(GameStates.main_menu, Text(text='О проекте'))
async def about_project(message: Message, session_maker):
    """
    Отправляем сообщения из БД о проекте

    """
    text = await get_text_about_project(session_maker)
    await message.answer(text, reply_markup=custom_kb('Главное меню'))


@main_router.message(GameStates.main_menu, Text(text='Начать игру'))
async def start_game(message: Message, state: FSMContext):
    """
    Начало игры. Отправляем первое слово

    """
    random_word = await get_first_random_word(state)
    await message.answer(f'{random_word}. Придумай слово на {get_last_letter(random_word).upper()}.',
                         reply_markup=custom_kb("Завершить игру"))
    await state.set_state(GameStates.waiting_word)
    await state.update_data(previous_word=random_word)
    await state.update_data(used_words=[random_word.lower()])


@main_router.message(GameStates.waiting_word)
async def game(message: Message, state: FSMContext, session_maker):
    """
    Логика игры

    """
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
    top_id_list = await get_top_id_list(session_maker)
    in_top = await check_user_in_top(message.from_user.id, session_maker)
    user_id = message.from_user.id
    if user_id in top_id_list and not in_top:
        await change_top_user(user_id, session_maker, True)
        await message.answer('Вы попали в топ-10 игроков. После завершения игры откройте рейтинг и оставьте сообщение'
                             ', которое увидят все.')
    if user_id not in top_id_list and in_top:
        await message.answer('Ты выпал из топ-10 игроков. Зарабатывай баллы и возвращайся в топ.')
        await change_top_user(user_id, session_maker, False)


@main_router.message(GameStates.main_menu, Text(text='Рейтинг'))
async def rating(message: Message, state: FSMContext, session_maker):
    """
    Отправляем сообщения администратора и рейтинг игроков

    """
    await state.set_state(GameStates.rating)
    text = await get_top_text(session_maker)
    admin_text = await get_admin_text(session_maker)
    top_id_list = await get_top_id_list(session_maker)
    await message.answer(text, disable_web_page_preview=True)
    if admin_text:
        await message.answer(admin_text, disable_web_page_preview=True)
    if message.from_user.id not in top_id_list:
        user_points = await get_user_points(message.from_user.id, session_maker)
        await message.answer(f"Сейчас у тебя {user_points} баллов. Играй активнее и попади в топ.")
    await message.answer("Находясь в топе игроков, ты можешь оставить сообщение под своим ником"
                         " которое будут видеть все игроки",
                         reply_markup=custom_kb('Изменить сообщение', 'Главное меню')
                         )


@main_router.message(GameStates.rating, Text(text='Изменить сообщение'))
async def pre_change_msg(message: Message, state: FSMContext):
    """
    Начинаем изменение сообщения игрока в топе

    """
    await message.answer("Введи сообщение, которое будет отображаться под твоим ником в топе игроков.",
                         reply_markup=custom_kb("Главное меню"))
    await state.set_state(GameStates.change_msg)


@main_router.message(GameStates.change_msg)
async def check_msg(message: Message, state: FSMContext):
    """
    Проверяем проходит ли сообщение по размеру и запрашиваем подтверждение у пользователя

    """
    if len(message.text) > 200:
        await message.answer("Сообщение должно содержать не более 200 символов. Введи сообщение короче",
                             reply_markup=custom_kb("Главное меню"))
        return
    await message.answer(f"В топе игроков под твоим ником будет следующее сообщение:\n {message.text}\n\n"
                         f"Подтвердить данное сообщение? Если хочешь изменить его то нажми изменить.",
                         reply_markup=custom_kb("Подтвердить", "Изменить"))
    await state.update_data(user_message=message.text)
    await state.set_state(GameStates.check_msg)


@main_router.message(GameStates.check_msg, Text(text=['Подтвердить', 'Изменить']))
async def change_msg(message: Message, state: FSMContext, session_maker):
    """
    В случае подтверждения обновляем сообщение в бд, в ином случае отправляемся на первый этап изменения сообщения

    """
    if message.text == "Подтвердить":

        data = await state.get_data()
        await change_user_message(message.from_user.id, data.get("user_message"), session_maker)
        await state.set_data({})
        await message.answer("Отлично! Теперь твое сообщение будет отображаться в топе игроков.",
                             reply_markup=custom_kb("Главное меню"))
    else:
        await message.answer("Введи сообщение, которое будет отображаться под твоим нииком в топе игроков.",
                             reply_markup=custom_kb("Главное меню"))
        await state.set_state(GameStates.change_msg)
        await state.set_data({})
