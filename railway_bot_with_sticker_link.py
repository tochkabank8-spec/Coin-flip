import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import random
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "8751194567:AAGBwILxFurE83l1Bf_HnhmrrILDpjoDeJA"

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

class CoinGame(StatesGroup):
    waiting_for_choice = State()
    waiting_for_sticker = State()

user_stickers = {}

STICKER_PACK_URL = "https://t.me/addstickers/CoinFlipprivatbot"

def get_choice_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🦅 Орёл"), KeyboardButton(text="🪙 Решка")]
        ],
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "🎮 Добро пожаловать в игру 'Орёл и решка'!\n\n"
        "Команды:\n"
        "/play - Начать игру\n"
        "/set_stickers - Загрузить стикеры\n"
        "/help - Справка"
    )

@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "📖 Как играть:\n\n"
        "1. /set_stickers - загрузи два стикера (орла и решка)\n"
        "2. /play - начни игру\n"
        "3. Выбери орла или решку\n"
        "4. Смотри результат! 🎉"
    )

@dp.message(Command("set_stickers"))
async def set_stickers(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_stickers[user_id] = {}
    await state.set_state(CoinGame.waiting_for_sticker)
    
    # Отправляем ссылку на стикер-пак с кнопкой
    await message.answer(
        "📤 Отправь стикер для ОРЛА (первый)\n\n"
        "💡 Нет подходящих стикеров? "
        "[Добавь стикер-пак](https://t.me/addstickers/CoinFlipprivatbot)",
        parse_mode="Markdown"
    )

@dp.message(CoinGame.waiting_for_sticker)
async def handle_sticker(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if not message.sticker:
        await message.answer("❌ Это не стикер!")
        return
    
    sticker_file_id = message.sticker.file_id
    sticker_count = len(user_stickers.get(user_id, {}))
    
    if sticker_count == 0:
        user_stickers[user_id]['eagle'] = sticker_file_id
        await message.answer(
            "✅ Орёл сохранён!\n\n"
            "Теперь отправь стикер для РЕШКИ\n\n"
            "💡 Нет подходящих стикеров? "
            "[Добавь стикер-пак](https://t.me/addstickers/CoinFlipprivatbot)",
            parse_mode="Markdown"
        )
    elif sticker_count == 1:
        user_stickers[user_id]['tails'] = sticker_file_id
        await message.answer(
            "✅ Готово! Оба стикера загружены!\n\n"
            "Теперь используй /play чтобы начать игру 🎮",
            parse_mode="Markdown"
        )
        await state.clear()

@dp.message(Command("play"))
async def play(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id not in user_stickers or len(user_stickers[user_id]) < 2:
        await message.answer(
            "⚠️ Загрузи стикеры командой /set_stickers\n\n"
            "💡 Нет подходящих стикеров? "
            "[Добавь стикер-пак](https://t.me/addstickers/CoinFlipprivatbot)",
            parse_mode="Markdown"
        )
        return
    
    await state.set_state(CoinGame.waiting_for_choice)
    await message.answer("🎯 Выбери орла или решку!", reply_markup=get_choice_keyboard())

@dp.message(CoinGame.waiting_for_choice)
async def handle_choice(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_choice = message.text
    
    if user_choice == "🦅 Орёл":
        choice = "eagle"
        display = "🦅 Орёл"
    elif user_choice == "🪙 Решка":
        choice = "tails"
        display = "🪙 Решка"
    else:
        await message.answer("❌ Выбери орла или решку!")
        return
    
    result = random.choice(["eagle", "tails"])
    result_display = "🦅 Орёл" if result == "eagle" else "🪙 Решка"
    sticker_id = user_stickers[user_id][result]
    
    if choice == result:
        status = "🎉 ВЫИГРАЛ!"
    else:
        status = "😢 Проиграл..."
    
    await message.answer(
        f"Результат: {result_display}\n"
        f"Ты выбрал: {display}\n\n{status}"
    )
    
    await bot.send_sticker(chat_id=message.chat.id, sticker=sticker_id)
    await state.clear()
    await message.answer("Ещё раз? /play", reply_markup=types.ReplyKeyboardRemove())

@dp.message()
async def echo(message: types.Message):
    await message.answer("Используй: /play, /set_stickers, /help")

async def main():
    logger.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
