from aiogram import types
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from data import add_user, get_users, users, get_user, add_currency_to_list, remove_currency_in_list, sql_ban
import aiohttp
from ban import ban


bot = Bot(token='6192085937:AAGuEV_W_FaB8eyaWzqcvUJG-VM79MS3hB8')
dp = Dispatcher(bot)


async def on_startup(_):
    await get_users()


@dp.message_handler(commands=['start', 'help'])
async def start(message):
    await add_user(message)
    await get_user(message)
    await bot.send_message(message.chat.id, 'Команда для вызова меню: /menu \nДобавить валюту: /add (код валюты) \nУдалить валюту: /remove (код валюты) \n\nДоступные валюты можно посмотреть на сайте: https://www.coingecko.com/ru' )


@dp.message_handler(commands=['menu'])
async def menu(message):
    currencies = users[message.chat.id]['cryptocurrencies']
    markup = types.InlineKeyboardMarkup()
    for button_id, button_text in currencies.items():
        markup.add(types.InlineKeyboardButton(text=f'{button_text}', callback_data=f'id:{button_id}'))

    await message.answer('Ваше меню валют'.format(message.from_user), reply_markup=markup)


@dp.message_handler(commands=['add'])
async def add_currency_btn(message):
    cryptocurrencies = users[message.chat.id]['cryptocurrencies']
    add_currency = message.text.split(' ')[1]
    url = f'https://api.coingecko.com/api/v3/search?query={add_currency}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            currency_data = await resp.json()

    for coin in currency_data['coins']:
        if coin['symbol'].lower() == add_currency.lower():
            add_currency = coin['id'], f'{coin["name"]} ({coin["symbol"]})'
            break
    else:
        await message.answer(f'Валюта не найдена')
        return

    if cryptocurrencies.get(coin['id']) is None:
        users[message.chat.id]['cryptocurrencies'][add_currency[0]] = add_currency[1]
        await add_currency_to_list(message, add_currency)
        await message.answer(f'В ваше меню добавлена валютa: {add_currency[1]}, вы можете получить обновленный список валют через команду /menu')
        print(f'{message.chat.id} add {add_currency}')
    else:
        await message.answer(f'В вашем меню уже есть валюта {add_currency[1]}')


@dp.message_handler(commands=['remove'])
async def add_currency_btn(message):
    currency_del_symbol = message.text.split(' ')[1].lower()
    currencies = users[message.chat.id]['cryptocurrencies']
    currency_del_id = [i for i in currencies if currencies[i].lower().split(' ')[-1] == f"({currency_del_symbol})"][0]
    currency_del_name = users[message.chat.id]["cryptocurrencies"][currency_del_id]
    await message.answer(f'Из меню удалена валюта: {currency_del_name}, вы можете получить обновленный список валют через команду /menu')
    await remove_currency_in_list(message, currency_del_id, currency_del_name)
    del users[message.chat.id]['cryptocurrencies'][currency_del_id]
    print(f'{message.chat.id} remove {currency_del_name}')


@dp.callback_query_handler(lambda call: call.data.startswith('id:'))
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

executor.start_polling(dp, on_startup = on_startup)