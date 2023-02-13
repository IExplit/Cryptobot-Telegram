import sqlite3

users = {}


async def get_users():
    db = sqlite3.connect('database\\users.db')
    cursor = db.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        username TEXT,
        last_name TEXT,
        cryptocurrencies TEXT,
        time_point_upd_message_count INTEGER DEFAULT 0,
        message_count INTEGER DEFAULT 0,
        unban_point INTEGER DEFAULT 0)""")
    db.commit()

    users_db = cursor.execute(f'SELECT id, cryptocurrencies, time_point_upd_message_count, message_count, unban_point FROM users').fetchall()
    for user in users_db:
        users[user[0]] = {'cryptocurrencies': {}, 'time_point_upd_message_count': user[2],
                          'message_count': user[3], 'unban_point': user[4], }
        currency = {}
        cryptocurrencies = user[1].split(', ')
        for i in range(len(cryptocurrencies)):
            currency[i] = cryptocurrencies[i].split(' - ')
            users[user[0]]['cryptocurrencies'][currency[i][0]] = currency[i][1]


async def get_user(message):
    db = sqlite3.connect('database\\users.db')
    cursor = db.cursor()

    user = cursor.execute(f'SELECT id, cryptocurrencies, time_point_upd_message_count, message_count, unban_point FROM users WHERE id == {message.chat.id}').fetchall()[0]
    users[user[0]] = {'cryptocurrencies': {}, 'time_point_upd_message_count': user[2],
                      'message_count': user[3], 'unban_point': user[4], }
    currency = {}
    cryptocurrencies = user[1].split(', ')
    for i in range(len(cryptocurrencies)):
        currency[i] = cryptocurrencies[i].split(' - ')
        users[user[0]]['cryptocurrencies'][currency[i][0]] = currency[i][1]


async def add_user(message):
    db = sqlite3.connect('database\\users.db')
    cursor = db.cursor()

    cursor.execute(f'SELECT id FROM users WHERE id == {message.chat.id}')
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (message.chat.id, message.chat.first_name,
                                                                             message.chat.username, message.chat.last_name,
                                                                             'bitcoin - Bitcoin (BTC), ethereum - Ethereum (ETH), '
                                                                             'tether - Tether (USDT), binancecoin - BNB (BNB), '
                                                                             'usd-coin - USD Coin (USDC), ripple - XRP (XRP)',
                                                                             0, 0, 0))
        db.commit()


async def add_currency_to_list(message, add_currency):
    user = message.chat.id

    db = sqlite3.connect('database\\users.db')
    cursor = db.cursor()

    cryptocurrencies = cursor.execute(f'SELECT cryptocurrencies FROM users WHERE id == {user}').fetchall()[0][0]
    cryptocurrencies = f'{cryptocurrencies}, {add_currency[0]} - {add_currency[1]}'

    cursor.execute('UPDATE users SET cryptocurrencies == ? WHERE id == ?', (cryptocurrencies, user))
    db.commit()


async def remove_currency_in_list(message, id_currency, name_currency):
    user = message.chat.id
    currency_dbname = f'{id_currency} - {name_currency}'

    db = sqlite3.connect('database\\users.db')
    cursor = db.cursor()

    cryptocurrencies = cursor.execute(f'SELECT cryptocurrencies FROM users WHERE id == {user}').fetchall()[0][0].split(', ')
    cryptocurrencies.remove(currency_dbname)
    cryptocurrencies = ', '.join(cryptocurrencies)

    cursor.execute('UPDATE users SET cryptocurrencies == ? WHERE id == ?', (cryptocurrencies, user))
    db.commit()


async def sql_ban(message):
    user_id = message.chat.id
    user_ban_params = users[user_id]['time_point_upd_message_count'], users[user_id]['message_count'], users[user_id]['unban_point']

    db = sqlite3.connect('database\\users.db')
    cursor = db.cursor()
    cursor.execute('UPDATE users SET time_point_upd_message_count == ?, message_count == ?, unban_point == ? WHERE id == ?', (user_ban_params[0], user_ban_params[1], user_ban_params[2], user_id))
    db.commit()








