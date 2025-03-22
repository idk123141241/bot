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

# 🔹 Автоматическая рассылка манго каждые 20 минут
async def send_mango_message():
    while True:
        await asyncio.sleep(20 * 60)
        for group_id in active_groups:
            await issue_mango(group_id)

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

# 🔹 Команда /timeleft
@dp.message(Command("timeleft"))
async def timeleft(message: types.Message):
    chat_id = message.chat.id
    if chat_id not in last_eaters or not last_eaters[chat_id]["time"]:
        await message.answer("МАНГО МОЖНО ЕБАТЬ! ЖДИТЕ СЛЕДУЮЩЕЙ ЁБЛИ!")
        return
    remaining_time = last_eaters[chat_id]["time"] - datetime.now()
    total_seconds = int(remaining_time.total_seconds())
    if total_seconds <= 0:
        await message.answer("МАНГО УЖЕ МОЖНО ВЫЕБАТЬ ALO")
        return
    minutes, seconds = divmod(total_seconds, 60)
    await message.answer(f"ДО СЛЕДУЮЩЕЙ ЁБЛИ ОСТАЛОСЬ: {minutes} МИНУТ {seconds} СЕКУНД! ⏳")

# 🔹 Обработка согласия
@dp.callback_query(F.data == "agree")
async def agree(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    user = callback_query.from_user
    if user.full_name in ["𝐍𝐨𝐧𝐞𝐥𝐨𝐩"]:
        await callback_query.answer(NONElOP_MESSAGE, show_alert=True)
        return
    if last_eaters.get(chat_id) and last_eaters[chat_id]["user_id"]:
        await callback_query.answer("МАНГО УЖЕ ВЫЕБАЛИ ALOO!", show_alert=True)
        return
    last_eaters[chat_id] = {"user_id": user.id, "time": datetime.now() + timedelta(minutes=20)}
    mango_stats[user.full_name] = mango_stats.get(user.full_name, 0) + 1
    save_stats()
    
    bot_profile_photos = await bot.get_user_profile_photos(bot.id)
    if bot_profile_photos.total_count > 0:
        bot_photo_id = bot_profile_photos.photos[0][0].file_id
        await bot.send_photo(chat_id, bot_photo_id, caption=f"{user.full_name} ВЫЕБАЛ МАНГО ПЕРВЫЙ! 🥭🎉")
    else:
        await bot.send_message(chat_id, f"{user.full_name} ВЫЕБАЛ МАНГО ПЕРВЫЙ! 🥭🎉")
    
    await callback_query.answer()

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
async def on_startup(bot: Bot):
    webhook_url = f"https://your-app-name.onrender.com/webhook"
    await bot.set_webhook(webhook_url)

app = web.Application()
dp.startup.register(on_startup)
SimpleRequestHandler(dp, bot).register(app, path="/webhook")
setup_application(app, dp)

# 🔹 Запуск сервера
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
