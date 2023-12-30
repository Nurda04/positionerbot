from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
import config
import database as db


storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)


class ProfileStatesGroup(StatesGroup):

    start_name = State()
    confirm_name = State()
    set_position = State()
    set_direction = State()
    get_position = State()


async def on_startup(_):
    db.db_start()
    print('Бот успешно запущен!')


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    db.cmd_start_db(message.from_user.id)
    await message.reply(f'{message.from_user.first_name}, Введите имя для регистрации')
    await ProfileStatesGroup.start_name.set()
    

@dp.message_handler(state=ProfileStatesGroup.start_name)
async def confirm_name(message: types.Message, state: FSMContext):
    item1 = types.InlineKeyboardButton('Да', callback_data='yes')
    item2 = types.InlineKeyboardButton('Нет', callback_data='no')
    markup = types.InlineKeyboardMarkup().add(item1, item2)
    global name
    name = message.text
    await message.reply(f'Ваше имя {name}?', reply_markup=markup)
    await ProfileStatesGroup.confirm_name.set()


@dp.callback_query_handler(state=ProfileStatesGroup.confirm_name)
async def callback_confirm_name(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'yes':
        text = f'Отлично, {name} вы внесены в базу'
        db.db_name(callback_query.from_user.id, name)
        await state.reset_state()
    elif callback_query.data == 'no':
        text = 'Введите имя для регистрации'
        await ProfileStatesGroup.start_name.set()
    await bot.send_message(chat_id=callback_query.message.chat.id, text=text)
    await callback_query.message.delete()


@dp.message_handler(commands=['at'])
async def cmd_set_position(message: types.Message):
    cmd_variants = ('/at')
    pos = message.text
    operation = "at"

    if not db.db_check_registr(message.from_user.id):
        text = "Вы не прошли регистрацию, команда /start"
    else:

        if pos == "/at@positionerbot":
            text = "Укажите ваше местоположение"
            await ProfileStatesGroup.set_position.set()
        else:
            for i in cmd_variants:
                pos = pos.replace(i, '').strip()

            if not pos:
                text = "Укажите ваше местоположение"
                await ProfileStatesGroup.set_position.set()
            else:
                db.db_set_position(message.from_user.id, operation, pos)
                text = f"Местоположение {pos} записано!"
    await message.reply(text)


@dp.message_handler(state=ProfileStatesGroup.set_position)
async def set_position(message: types.Message, state: FSMContext):
    pos = message.text
    operation = "at"

    db.db_set_position(message.from_user.id, operation, pos)
    await message.reply(f"Местоположение {pos} записано!")
    await state.reset_state()


@dp.message_handler(commands=['go'])
async def cmd_set_direction(message: types.Message):
    cmd_variants = ('/go')
    pos = message.text
    operation = "go"

    if not db.db_check_registr(message.from_user.id):
        text = "Вы не прошли регистрацию, команда /start"
    else:

        if pos == '/go@positionerbot':
            text = "Укажите ваше направление"
            await ProfileStatesGroup.set_direction.set()
        else:
            for i in cmd_variants:
                pos = pos.replace(i, '').strip()

            if not pos:
                text = "Укажите ваше направление"
                await ProfileStatesGroup.set_direction.set()
            else:
                db.db_set_position(message.from_user.id, operation, pos)
                text = f"Направление {pos} записано!"
    await message.reply(text)


@dp.message_handler(state=ProfileStatesGroup.set_direction)
async def set_direction(message: types.Message, state: FSMContext):
    pos = message.text
    operation = "go"

    db.db_set_position(message.from_user.id, operation, pos)
    await message.reply(f"Направление {pos} записано!")
    await state.reset_state()


def get_position2(pos_name)->(str):
    check_at = db.db_check_at(pos_name)
    check_go = db.db_check_go(pos_name)
    position_at = db.db_get_position_at(pos_name)
    position_go = db.db_get_position_go(pos_name)

    if not check_go:
        if not check_at:
            text = f"Нет записей по имени {pos_name}"
        else: text = f'Местоположение {pos_name}\nГде - ' + position_at[0] + ', ' + position_at[1]
    else:
        if not check_at:
            text = f'Местоположение {pos_name}\nКуда - ' + position_go[0] + ', ' + position_go[1]
        else: 
            if position_at[1] <= position_go[1]:
                text = f'Местоположение {pos_name}\nГде - ' + (position_at[0] + ', ' + position_at[1]) + '\nКуда - ' + (position_go[0] + ', ' + position_go[1])
            else: text = f'Местоположение {pos_name}\nГде - ' + position_at[0] + ', ' + position_at[1]
    return text


@dp.message_handler(commands=['where', 'wh'])
async def cmd_get_position(message: types.Message):
    cmd_variants = ('/where', '/wh')
    pos_name = message.text

    for i in cmd_variants:
        pos_name = pos_name.replace(i, '').strip()

    if not pos_name or pos_name == "@positionerbot":
        text = "Укажите имя пользователя о местоположении которого вы хотите узнать"
        await ProfileStatesGroup.get_position.set()
    else:
        check_name = db.db_check_name(pos_name)
        if not check_name:
            text = f"Нет пользователя по имени {pos_name}"
        else: 
            text = get_position2(pos_name)
    await message.reply(text)
     

@dp.message_handler(state=ProfileStatesGroup.get_position)
async def get_position(message: types.Message, state: FSMContext):
    pos_name = message.text

    check_name = db.db_check_name(pos_name)
    if not check_name:
        text = f"Нет пользователя по имени {pos_name}"
    else: 
        text = get_position2(pos_name)
    await message.reply(text)
    await state.reset_state()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)