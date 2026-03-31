import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import random
import os
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8751194567:AAFCWkorfLJBh6-HTBlfsENf8YPUysw_WO4"

# Инициализация
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

# Состояния для FSM
class CoinGame(StatesGroup):
    waiting_for_choice = State()
    waiting_for_sticker = State()

# Хранилище стикеров
user_stickers = {}

# Клавиатура
def get_choice_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🦅 Орёл"), KeyboardButton(text="🪙 Решка")]
        ],
        resize_keyboard=True
    )
    return keyboard

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer(
        "🎮 Добро пожаловать в игру 'Орёл и решка'!\n\n"
        "Команды:\n"
        "/play - Начать игру\n"
        "/set_stickers - Загрузить стикеры для орла и решки\n"
        "/help - Справка"
    )

@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "📖 Как играть:\n\n"
        "1. Используй /set_stickers чтобы загрузить два стикера:\n"
        "   - Первый для орла\n"
        "   - Второй для решки\n\n"
        "2. Используй /play чтобы начать игру\n"
        "3. Выбери орла или решку\n"
        "4. Бот покажет результат со стикером\n\n"
        "Удачи! 🍀"
    )

@dp.message(Command("set_stickers"))
async def set_stickers(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_stickers[user_id] = {}
    await state.set_state(CoinGame.waiting_for_sticker)
    await message.answer(
        "📤 Отправь стикер для ОРЛА (первый)",
        reply_markup=types.ReplyKeyboardRemove()
    )

@dp.message(CoinGame.waiting_for_sticker)
async def handle_sticker(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if not message.sticker:
        await message.answer("❌ Это не стикер. Пожалуйста, отправь стикер.")
        return
    
    sticker_file_id = message.sticker.file_id
    sticker_count = len(user_stickers.get(user_id, {}))
    
    if sticker_count == 0:
        user_stickers[user_id]['eagle'] = sticker_file_id
        await message.answer(
            f"✅ Стикер для орла сохранён!\n\n"
            f"Теперь отправь стикер для РЕШКИ (второй)"
        )
    elif sticker_count == 1:
        user_stickers[user_id]['tails'] = sticker_file_id
        await message.answer(
            "✅ Отлично! Оба стикера загружены!\n\n"
            "Теперь ты можешь играть. Используй /play"
        )
        await state.clear()
    else:
        await message.answer("❌ Что-то пошло не так. Используй /set_stickers чтобы начать заново.")

@dp.message(Command("play"))
async def play(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id not in user_stickers or len(user_stickers[user_id]) < 2:
        await message.answer(
            "⚠️ Сначала загрузи стикеры!\n\n"
            "Используй /set_stickers"
        )
        return
    
    await state.set_state(CoinGame.waiting_for_choice)
    await message.answer(
        "🎯 Выбери орла или решку!",
        reply_markup=get_choice_keyboard()
    )

@dp.message(CoinGame.waiting_for_choice)
async def handle_choice(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_choice = message.text
    
    if user_choice == "🦅 Орёл":
        choice = "eagle"
        display_choice = "🦅 Орёл"
    elif user_choice == "🪙 Решка":
        choice = "tails"
        display_choice = "🪙 Решка"
    else:
        await message.answer("❌ Выбери либо орла либо решку!")
        return
    
    result = random.choice(["eagle", "tails"])
    result_display = "🦅 Орёл" if result == "eagle" else "🪙 Решка"
    sticker_file_id = user_stickers[user_id][result]
    
    if choice == result:
        status = "🎉 ТЫ ВЫИГРАЛ!"
    else:
        status = "😢 Ты проиграл..."
    
    await message.answer(
        f"💫 Результат: {result_display}\n"
        f"Ты выбрал: {display_choice}\n\n"
        f"{status}"
    )
    
    await bot.send_sticker(
        chat_id=message.chat.id,
        sticker=sticker_file_id
    )
    
    await state.clear()
    await message.answer(
        "🎮 Хочешь ещё раз? Используй /play",
        reply_markup=types.ReplyKeyboardRemove()
    )

# Обработка всех остальных сообщений
@dp.message()
async def echo(message: types.Message):
    await message.answer("Используй команды: /play, /set_stickers, /help")

async def main():
    """Запуск бота"""
    logger.info("🚀 Бот запущен на Railway...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    asyncio.run(main())
