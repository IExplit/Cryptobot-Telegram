import aiohttp
from database.editdata import users, add_currency_to_list, remove_currency_in_list


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
    else:
        await message.answer(f'В вашем меню уже есть валюта {add_currency[1]}')


async def remove_currency_btn(message):
    currency_del_symbol = message.text.split(' ')[1].lower()
    currencies = users[message.chat.id]['cryptocurrencies']
    currency_del_id = [i for i in currencies if currencies[i].lower().split(' ')[-1] == f"({currency_del_symbol})"][0]
    currency_del_name = users[message.chat.id]["cryptocurrencies"][currency_del_id]
    await message.answer(f'Из меню удалена валюта: {currency_del_name}, вы можете получить обновленный список валют через команду /menu')
    await remove_currency_in_list(message, currency_del_id, currency_del_name)
    del users[message.chat.id]['cryptocurrencies'][currency_del_id]