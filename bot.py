import os
import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime, timedelta
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# 🔹 Загружаем токен из переменных окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🔹 Данные для хранения статистики
active_groups = set()
last_eaters = {}
mango_stats_file = "mango_stats.json"

try:
    with open(mango_stats_file, "r") as file:
        mango_stats = json.load(file)
except FileNotFoundError:
    mango_stats = {}

NONElOP_MESSAGE = "ПОШЕЛ НАХУЙ!🍑🚫"

# 🔹 Функция сохранения статистики
def save_stats():
    with open(mango_stats_file, "w") as file:
        json.dump(mango_stats, file)

# 🔹 Кнопки
def get_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="СОГЛАСИТЬСЯ ✅✅✅", callback_data="agree")],
            [InlineKeyboardButton(text="ОТКАЗАТЬСЯ ❌❌❌", callback_data="decline")]
        ]
    )

# 🔹 Выдача манго
async def issue_mango(chat_id):
    last_eaters[chat_id] = {"user_id": None, "time": datetime.now() + timedelta(minutes=20)}
    await bot.send_message(
        chat_id,
        "ВСЕХ ПРИГЛАСИЛИ ЕБАТЬ МАНГО! КТО ПЕРВЫЙ? 🥭",
        reply_markup=get_keyboard()
    )

# 🔹 Команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        if message.chat.id in active_groups:
            await message.answer("БОТ УЖЕ АКТИВИРОВАН В ЭТОЙ ГРУППЕ! 🚫")
            return
        
        active_groups.add(message.chat.id)
        await issue_mango(message.chat.id)
        await message.answer("УСПЕШНАЯ АКТИВАЦИЯ БОТА✅🥭")
    else:
        await message.answer("Добавьте бота в группу и напишите /start")

# 🔹 Команда /topmango
@dp.message(Command("topmango"))
async def top_mango(message: types.Message):
    if not mango_stats:
        await message.answer("ПОКА НИКТО НЕ ВЫЕБАЛ МАНГО!🥭")
        return
    sorted_stats = sorted(mango_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    leaderboard = "🏆 ТОП 10 ЛЮДЕЙ ПО ЕБЛЕ МАНГО🥭:\n\n"
    for i, (user, count) in enumerate(sorted_stats, 1):
        leaderboard += f"{i}. {user} — {count} РАЗ🥭\n"
    await message.answer(leaderboard)

# 🔹 Настройка Webhook
async def on_startup():
    webhook_url = f"https://your-app-name.onrender.com/webhook"
    await bot.set_webhook(webhook_url)

# 🔹 Настройка API-сервера
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
setup_application(app, dp)

# 🔹 Запуск сервера
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(on_startup())  # ⬅️ Правильный вызов без аргументов
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
