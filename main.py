from aiogram.utils import executor
from crbot import dp
from database.editdata import get_users
from handlers.usermenu import menu, give_price
from handlers.editmenu import add_currency_btn, remove_currency_btn
from handlers.starting import start


async def on_startup(_):
    await get_users()

    
dp.register_message_handler(start, commands=['start', 'help'])
dp.register_message_handler(menu, commands=['menu'])
dp.register_callback_query_handler(give_price, lambda call: call.data.startswith('id:'))
dp.register_message_handler(add_currency_btn, commands=['add'])
dp.register_message_handler(remove_currency_btn, commands=['remove'])
executor.start_polling(dp, on_startup=on_startup)
