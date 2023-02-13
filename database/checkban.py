from database.editdata import users


async def ban(message):

    user_id = message.chat.id
    message_date = int(message.date.now().timestamp())

    if users[user_id]['unban_point'] != 0:
        if users[user_id]['unban_point'] < message_date:
            users[user_id]['unban_point'] = 0
            users[user_id]['time_point_upd_message_count'] = message_date + 60
            users[user_id]['message_count'] = 1

    elif users[user_id]['unban_point'] == 0:
        if users[user_id]['time_point_upd_message_count'] <= message_date:
            users[user_id]['message_count'] = 1
            users[user_id]['time_point_upd_message_count'] = message_date + 60

        elif users[user_id]['message_count'] <= 5:
            users[user_id]['message_count'] += 1

        if users[user_id]['message_count'] > 5:
            users[user_id]['unban_point'] = message_date + 600