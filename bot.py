import os
import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Файл статистики
mango_stats_file = "mango_stats.json"
try:
    with open(mango_stats_file, "r") as file:
        mango_stats = json.load(file)
except FileNotFoundError:
    mango_stats = {}

# Команда /start
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Бот работает через Webhook! 🚀")

# Установка Webhook
async def on_startup():
    webhook_url = f"{os.getenv('WEBHOOK_URL')}/webhook"  # БЕРЁМ ИЗ ENV
    await bot.set_webhook(webhook_url)
    logging.info(f"📡 Webhook установлен: {webhook_url}")

# Настройка веб-сервера
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
setup_application(app, dp)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(on_startup())  # СТАВИМ Webhook
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
