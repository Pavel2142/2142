import asyncio
from datetime import datetime
from telethon import TelegramClient, events, types
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji

# Ваши данные для авторизации
api_id = '22101462'  # Замените на ваш API ID
api_hash = 'cc6369b9c1916ebaaeb7ab76b0a76ce5'  # Замените на ваш API Hash
log_channel_id = -1002269320153  # Замените на ваш ID канала или группы
users_to_track = ['Jennie1075', 'lilyhusbenddd', 'wdhxk']  # Добавляем wdhxk в список отслеживаемых пользователей

# Инициализация клиента для вашего аккаунта
client = TelegramClient('session_name', api_id, api_hash)

# Храним данные о статусе пользователей
user_status = {username: False for username in users_to_track}
user_start_times = {username: None for username in users_to_track}
start_time = None  # Время, когда оба пользователя стали онлайн

# Функция для отправки сообщений в канал с добавлением реакции
async def send_log_to_channel(message):
    try:
        sent_message = await client.send_message(log_channel_id, message)
        # Добавляем реакцию клоуна к только что отправленному сообщению
        await add_reaction(sent_message)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в канал: {e}")

# Функция для добавления реакции клоуна с аккаунта на сообщение
async def add_reaction(message):
    try:
        # Добавляем реакцию клоуна с аккаунта на сообщение
        reaction = ReactionEmoji(emoticon='🤡')
        await client(SendReactionRequest(
            peer=message.peer_id,
            msg_id=message.id,
            reaction=[reaction]
        ))
    except Exception as e:
        print(f"Ошибка при добавлении реакции к сообщению: {e}")

# Функция для добавления реакции к любому входящему сообщению
@client.on(events.NewMessage)
async def add_reaction_to_any_message(event):
    try:
        # Добавляем реакцию клоуна с аккаунта на любое входящее сообщение
        await add_reaction(event.message)
    except Exception as e:
        print(f"Ошибка при добавлении реакции к сообщению: {e}")

# Функция для отслеживания статуса пользователей
async def check_online_status():
    global start_time
    while True:
        status_list = []  # Список для формирования статусов пользователей
        for username in users_to_track:
            try:
                user = await client.get_entity(username)
                online_now = isinstance(user.status, types.UserStatusOnline)

                # Если пользователь стал онлайн
                if online_now and not user_status[username]:
                    user_start_times[username] = datetime.now()
                    log_message = f"{username} стал онлайн\n" \
                                  f"Время: {user_start_times[username].strftime('%H:%M:%S')} 🤡 #{username}"
                    await send_log_to_channel(log_message)

                # Если пользователь стал оффлайн
                elif not online_now and user_status[username]:
                    end_time = datetime.now()
                    log_message = f"{username} был онлайн с {user_start_times[username].strftime('%H:%M:%S')} до {end_time.strftime('%H:%M:%S')}\n" \
                                  f"Время онлайн: {str(end_time - user_start_times[username]).split('.')[0]} 🤡 #{username}"
                    await send_log_to_channel(log_message)
                    user_start_times[username] = None

                user_status[username] = online_now

                # Формируем строку для вывода в консоль
                status = "Онлайн" if online_now else "Оффлайн"
                status_list.append(f"{username}: {status}")

            except Exception as e:
                print(f"Ошибка при получении данных о {username}: {e}")

        # Выводим в консоль текущий статус всех пользователей
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\033[92mПроверка статуса пользователей: {current_time} ({', '.join(status_list)})\033[0m")

        # Проверка для обоих пользователей
        if all(user_status.values()):
            if start_time is None:
                start_time = datetime.now()
                log_message = f"Оба пользователя стали онлайн с {start_time.strftime('%H:%M:%S')}\n🤡 #Пон"
                await send_log_to_channel(log_message)

        elif start_time is not None:
            end_time = datetime.now()
            log_message = f"Оба пользователя были онлайн с {start_time.strftime('%H:%M:%S')} до {end_time.strftime('%H:%M:%S')}\n" \
                          f"Общее время онлайн: {str(end_time - start_time).split('.')[0]} 🤡 #Пон"
            await send_log_to_channel(log_message)
            start_time = None

        await asyncio.sleep(10)

# Основная асинхронная функция для запуска клиента и проверки статуса
async def main():
    await client.start()  # Авторизация в аккаунте
    await check_online_status()

# Запускаем основной цикл
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
