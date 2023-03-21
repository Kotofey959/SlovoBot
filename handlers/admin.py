from aiogram import Router, Bot
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from db.admin_msg import get_msg_text, change_msg
from db.users import get_user, get_users_count, check_admin, get_admins_list_text, del_admin_from_db, add_admin_to_db, \
    get_user_by_name, get_all_users_id
from helper import get_admin_username, new_words_to_list, add_new_words, check_words_in_dict
from keyboards.main import custom_kb, del_admin_kb

admin_router = Router()


class AdminState(StatesGroup):
    admin = State()
    del_admin = State()
    add_admin = State()
    admin_msg = State()
    check_msg = State()
    confirm_msg = State()
    mailing = State()
    confirm_mail = State()
    wait_words = State()
    confirm_words = State()


@admin_router.message(Text(text=["admin", "Админ панель"]))
async def admin_panel(message: Message, state: FSMContext, session_maker):
    await state.set_data({})
    if not await check_admin(message.from_user.id, session_maker):
        await message.answer("Я тебя не понимаю, воспользуйся клавиатурой бота", reply_markup=custom_kb("Главное меню"))
        return
    await state.set_state(AdminState.admin)
    await message.answer("Что хотим сделать",
                         reply_markup=custom_kb("Изменить сообщения в топе", "Узнать кол-во игроков",
                                                "Добавить администратора", "Удалить администратора",
                                                "Рассылка пользователям", "Добавить новые слова"))


@admin_router.message(AdminState.admin, Text(text="Узнать кол-во игроков"))
async def users_count(message: Message, session_maker):
    count = await get_users_count(session_maker)
    await message.answer(f"Кол-во игроков: {count}", reply_markup=custom_kb("Админ панель"))


@admin_router.message(AdminState.admin, Text(text="Удалить администратора"))
async def del_admin(message: Message, state: FSMContext, session_maker):
    admin_list = await get_admins_list_text(session_maker)
    text = ''
    for admin in admin_list:
        text += f"{admin}\n"

    await message.answer(f"Вот список администраторов:\n"
                         f"{text}"
                         f"Кого необходимо удалить?",
                         reply_markup=del_admin_kb(admin_list))
    await state.set_state(AdminState.del_admin)


@admin_router.message(AdminState.del_admin)
async def choose_admin(message: Message, state: FSMContext, session_maker):
    admin_username = await get_admin_username(message.text, session_maker)
    admin_list = await get_admins_list_text(session_maker)
    if not admin_username:
        await message.answer("Я тебя не понимаю, воспользуйся клавиатурой бота", reply_markup=del_admin_kb(admin_list))
        return
    if message.from_user.username == admin_username:
        await message.answer("Нельзя убрать себя из администраторов, выбери другого человека",
                             reply_markup=del_admin_kb(admin_list))
        return

    await del_admin_from_db(admin_username, session_maker)
    await message.answer(f"Администратор {message.text} удален", reply_markup=custom_kb("Админ панель"))
    await state.set_state(AdminState.admin)


@admin_router.message(AdminState.admin, Text(text="Добавить администратора"))
async def add_admin(message: Message, state: FSMContext):
    await message.answer("Введите username аккаунта без @, которого нужно сделать администратором.",
                         reply_markup=custom_kb("Админ панель"))
    await state.set_state(AdminState.add_admin)


@admin_router.message(AdminState.add_admin)
async def await_admin_id(message: Message, session_maker):
    text = message.text
    if not await get_user_by_name(text, session_maker):
        await message.answer("Пользователь с таким логином не пользуется ботом. Введите верный логин",
                             reply_markup=custom_kb("Админ панель"))
        return
    await add_admin_to_db(text, session_maker)
    await message.answer(f"Аккаунт {text} добавлен в список администраторов",
                         reply_markup=custom_kb("Админ панель"))


@admin_router.message(AdminState.admin, Text(text="Изменить сообщения в топе"))
async def change_admin_msg(message: Message, state: FSMContext, session_maker):
    msg1 = await get_msg_text('Сообщение №1', session_maker)
    msg2 = await get_msg_text('Сообщение №2', session_maker)
    msg3 = await get_msg_text('Сообщение №3', session_maker)
    await message.answer(f"Вот ваши сообщения в топе:\n"
                         f"1)\n{msg1}\n"
                         f"2)\n{msg2}\n"
                         f"3)\n{msg3}\n"
                         f"Какое из сообщений вы хотите изменить?",
                         reply_markup=custom_kb("Сообщение №1", "Сообщение №2", "Сообщение №3", "Админ панель"))
    await state.set_state(AdminState.admin_msg)


@admin_router.message(AdminState.admin_msg)
async def waiting_msg(message: Message, state: FSMContext, session_maker):
    if message.text not in ['Сообщение №1', 'Сообщение №2', 'Сообщение №3']:
        await message.answer("Выбери сообщение, которое хочешь изменить, используя клавиатуру бота",
                             reply_markup=custom_kb("Сообщение №1", "Сообщение №2", "Сообщение №3", "Админ панель"))
        return
    await message.answer(f"Введите сообщение, которое должно отображаться в {message.text}",
                         reply_markup=custom_kb("Админ панель"))
    await state.set_state(AdminState.check_msg)
    await state.update_data(adm_msg=message.text)


@admin_router.message(AdminState.check_msg)
async def check_msg(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(msg=message.text)
    await message.answer(f'{data.get("adm_msg")} будет изменено на:\n {message.text}\n\n'
                         f'Подтвердить изменения? Если текст неверный нажми изменить',
                         reply_markup=custom_kb("Подтвердить", "Изменить"))
    await state.set_state(AdminState.confirm_msg)


@admin_router.message(AdminState.confirm_msg, Text(text=['Подтвердить', 'Изменить']))
async def confirm_msg(message: Message, state: FSMContext, session_maker):
    data = await state.get_data()
    if message.text == 'Подтвердить':
        await change_msg(data.get("adm_msg"), data.get("msg"), session_maker)
        await message.answer(f"Сообщение {data.get('adm_msg')} успешно изменено",
                             reply_markup=custom_kb("Админ панель"))
        await state.set_state(AdminState.admin)
        await state.set_data({})
    else:
        await message.answer(f"Введите сообщение, которое должно отображаться в {data.get('adm_msg')}",
                             reply_markup=custom_kb("Админ панель"))
        await state.set_state(AdminState.check_msg)


@admin_router.message(AdminState.admin, Text(text="Рассылка пользователям"))
async def mailing(message: Message, state: FSMContext):
    await message.answer("Введите текст, который необходимо отправить пользователям",
                         reply_markup=custom_kb("Админ панель"))
    await state.set_state(AdminState.mailing)


@admin_router.message(AdminState.mailing)
async def wait_mail(message: Message, state: FSMContext):
    await state.update_data(mail=message.text)
    await message.answer(f"Всем пользователям будет отправлено сообщение:\n{message.text}\n\n"
                         f"Подтвердить или изменить сообщение?",
                         reply_markup=custom_kb("Подтвердить", "Изменить"))
    await state.set_state(AdminState.confirm_mail)


@admin_router.message(AdminState.confirm_mail, Text(text=['Подтвердить', 'Изменить']))
async def confirm_mail(message: Message, state: FSMContext, session_maker, bot: Bot):
    if message.text == 'Подтвердить':
        id_list = await get_all_users_id(session_maker)
        data = await state.get_data()
        for id in id_list:
            await bot.send_message(id, data.get("mail"))
        await message.answer(f"Ваше сообщение отправлено всем пользователям",
                             reply_markup=custom_kb("Админ панель"))
        await state.set_state(AdminState.admin)
        await state.set_data({})
    else:
        await message.answer("Введите текст, который необходимо отправить пользователям",
                             reply_markup=custom_kb("Админ панель"))
        await state.set_state(AdminState.mailing)


@admin_router.message(AdminState.admin, Text(text="Добавить новые слова"))
async def new_words(message: Message, state: FSMContext):
    await message.answer("Отправьте слова, которые нужно добавить. Если слов несколько, укажите их через запятую.",
                         reply_markup=custom_kb("Админ панель"))
    await state.set_state(AdminState.wait_words)


@admin_router.message(AdminState.wait_words)
async def check_words(message: Message, state: FSMContext):
    invalid_words = check_words_in_dict(new_words_to_list(message.text))
    if invalid_words:
        await message.answer(f"Слова {invalid_words} уже есть в словаре.")
        await message.answer("Отправьте слова, которые нужно добавить. Если слов несколько, укажите их через запятую.",
                             reply_markup=custom_kb("Админ панель"))
        return
    await message.answer(f"Следующие слова: {message.text} будут добавлены в словарь, подтвердить или изменить?",
                         reply_markup=custom_kb("Подтвердить", "Изменить"))
    await state.update_data(words=new_words_to_list(message.text))
    await state.set_state(AdminState.confirm_words)


@admin_router.message(AdminState.confirm_words, Text(text=['Подтвердить', 'Изменить']))
async def confirm_words(message: Message, state: FSMContext):
    if message.text == 'Подтвердить':
        data = await state.get_data()
        add_new_words(data.get("words"))
        await message.answer(f"Слова {data.get('words')} успешно добавлены в словарь",
                             reply_markup=custom_kb("Админ панель"))
    else:
        await message.answer("Отправьте слова, которые нужно добавить. Если слов несколько, укажите их через запятую.",
                             reply_markup=custom_kb("Админ панель"))
        await state.set_state(AdminState.wait_words)
