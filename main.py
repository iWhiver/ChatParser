import asyncio
import configparser
from json import loads
from pyrogram import Client, errors, enums

from bd import Sql_lite

config = configparser.ConfigParser()  # создаём объекта парсера
config.read(".ini")  # читаем конфиг


BOT_TOKEN = config['Config']['BOT_TOKEN']
API_ID = config['Config']['API_ID']
API_HASH = config['Config']['API_HASH']
PHONE_NUMBER = config['Config']['PHONE']
PASSWORD = config['Config']['PASSWORD']
FLAG = config['Config']['FLAG']

if FLAG == 'True':
    db = Sql_lite(FLAG)

chats = [
    'mediasocialmarket',
    'terncrypto_otc',
    'MarketICOBOG'
]

# doubletop - чат, который банит виртуальные аккаунты

counter = 0

data = []


def search_text(text: str) -> bool:
    """Поиск элемента в массиве"""
    if text in data:
        return True
    else:
        return False


def delete_text_from_data():
    """Удаление последнего элемента массива, если длина массива превысит 1000 элементов"""
    while True:
        print(f'В массиве {len(data)} записей')
        if len(data) < 1001:
            break
        a = data.pop(-1)


def create_a_message(id_user, title_chat, first_name, last_name, username, text):
    """Создание сообщения пользователю"""
    html_id_user = f'<a href="tg://user?id={id_user}">{id_user}</a>'
    message = f'Chat: {title_chat}\nId user: {html_id_user}\nFirst name: {first_name}\nLast name: ' \
              f'{last_name}\nUsername: {username}\nText: {text}'
    return message


async def main(array: list) -> None:
    """Обработка чатов, занесение данных в БД или в массив, вывод собщений в избранное"""
    global counter
    count = 0
    async with Client("my_account", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE_NUMBER, password=PASSWORD) as \
            app:
        try:
            for el in array:
                async for message in app.get_chat_history(el, limit=50):
                    dict_message = loads(str(message))
                    title_chat = dict_message['chat']['title']
                    id_user = int(dict_message['from_user']['id'])
                    first_name = 'Неизвестно'
                    if 'first_name' in dict_message['from_user']:
                        first_name = dict_message['from_user']['first_name']
                    last_name = 'Неизвестно'
                    if 'last_name' in dict_message['from_user']:
                        last_name = dict_message['from_user']['last_name']
                    username = 'Неизвестно'
                    if 'username' in dict_message['from_user']:
                        username = dict_message['from_user']['username']
                    date = dict_message['date']
                    text = dict_message['text']
                    if FLAG == 'True':
                        if (('wts' in text.lower() and 'binance' in text.lower()) or ('wtb' in text.lower() and
                                                                                      'binance' in text.lower())) and \
                                db.finding_a_duplicate_entry_in_the_database(text) is False:
                            counter += 1
                            db.write_to_the_database(
                                id=counter,
                                chat=title_chat,
                                id_user=id_user,
                                first_name=first_name,
                                last_name=last_name,
                                username=username,
                                date=date,
                                text=text
                            )
                            message = create_a_message(id_user, title_chat, first_name, last_name, username, text)
                            count += 1
                            await app.send_message("me", message, parse_mode=enums.ParseMode.HTML)
                    else:
                        if (('wts' in text.lower() and 'binance' in text.lower()) or ('wtb' in text.lower() and
                                                                                      'binance' in text.lower())) and \
                                search_text(text) is False:
                            if text not in data:
                                data.append(text)
                            message = create_a_message(id_user, title_chat, first_name, last_name, username, text)
                            await app.send_message("me", message, parse_mode=enums.ParseMode.HTML)
                await asyncio.sleep(3)
        except errors.exceptions.flood_420.FloodWait as wait_err:
            await asyncio.sleep(wait_err.value)
    if FLAG == 'True':
        print(f'В БД занесено {count} записей, в этом цикле')

while True:
    asyncio.run(main(chats))
    delete_text_from_data()
    if FLAG == 'True':
        db.deleting_extra_entries()
