import aiohttp
from aiogram import types
from database.editdata import users, sql_ban
from database.checkban import ban


async def menu(message):
    currencies = users[message.chat.id]['cryptocurrencies']
    markup = types.InlineKeyboardMarkup()
    for button_id, button_text in currencies.items():
        markup.add(types.InlineKeyboardButton(text=f'{button_text}', callback_data=f'id:{button_id}'))

    await message.answer('Ваше меню валют'.format(message.from_user), reply_markup=markup)


async def give_price(callback):
    user_id = callback.message.chat.id
    currencies = users[callback.message.chat.id]['cryptocurrencies']
    button_id = callback.data.split(':')[1]
    button_text = currencies.get(button_id)
    if button_text is not None:
        await ban(callback.message)
        await sql_ban(callback.message)
        if users[user_id]['unban_point'] == 0:
            url = f'https://api.coingecko.com/api/v3/simple/price?ids={button_id}&vs_currencies=rub'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    price = await resp.json()
            price = round(int(price[button_id]['rub']))
            await callback.message.answer(f'Текущая стоимость {button_text} - {price} RUB')

        else:
            if users[user_id]["unban_point"] - callback.message.date.now().second <= 60:
                await callback.message.answer(f'Предельная скорость отправки сообщений была превышена. Вы снова сможете отправить запрос через несколько секунд')
            else:
                await callback.message.answer(f'Предельная скорость отправки сообщений была превышена. Вы снова сможете отправить запрос через {round((users[user_id]["unban_point"] - callback.message.date.now().timestamp()) / 60)} минут')

    else:
        await callback.message.answer('В вашем меню пока нет такой валюты')
    await callback.answer()