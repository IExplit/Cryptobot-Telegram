from crbot import bot
from database.editdata import  add_user, get_user


async def start(message):
    await add_user(message)
    await get_user(message)
    await bot.send_message(message.chat.id, 'priv')