import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime, timedelta

TOKEN = "7801430904:AAEe1Wa6EHUsCDWmKMFLq8idT9ILMN2seY8"

bot = Bot(token=TOKEN)
dp = Dispatcher()

active_groups = set()
last_eaters = {}
mango_stats_file = "mango_stats.json"

try:
    with open(mango_stats_file, "r") as file:
        mango_stats = json.load(file)
except FileNotFoundError:
    mango_stats = {}

NONElOP_MESSAGE = "ПОШЕЛ НАХУЙ!🍑🚫"

def save_stats():
    with open(mango_stats_file, "w") as file:
        json.dump(mango_stats, file)

def get_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="СОГЛАСИТЬСЯ ✅✅✅", callback_data="agree")],
            [InlineKeyboardButton(text="ОТКАЗАТЬСЯ ❌❌❌", callback_data="decline")]
        ]
    )

async def send_mango_message():
    while True:
        await asyncio.sleep(20 * 60)
        for group_id in active_groups:
            await issue_mango(group_id)

async def issue_mango(chat_id):
    last_eaters[chat_id] = {"user_id": None, "time": datetime.now() + timedelta(minutes=20)}
    await bot.send_message(
        chat_id,
        "ВСЕХ ПРИГЛАСИЛИ ЕБАТЬ МАНГО! КТО ПЕРВЫЙ? 🥭",
        reply_markup=get_keyboard()
    )

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

async def console_listener():
    while True:
        user_input = await asyncio.to_thread(input)
        if user_input.strip() == "#выдатьманго":
            for group_id in active_groups:
                await issue_mango(group_id)
        elif user_input.startswith("!"):
            message_text = user_input[1:].strip()
            for group_id in active_groups:
                await bot.send_message(group_id, message_text)

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(send_mango_message())
    asyncio.create_task(console_listener())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 
