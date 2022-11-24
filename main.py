import asyncio
import configparser
import configparser
from os import getenv
from dotenv import load_dotenv
import sqlite3
from json import loads
from pyrogram import Client, errors, enums
# load_dotenv()

config = configparser.ConfigParser()  # создаём объекта парсера
config.read(".ini")  # читаем конфиг


# BOT_TOKEN = getenv('BOT_TOKEN')
# api_id = int(getenv('API_ID'))
# api_hash = getenv('API_HASH')
# phone_number = getenv('PHONE')
# password = getenv('PASSWORD')


BOT_TOKEN = config['Config']['BOT_TOKEN']
api_id = config['Config']['API_ID']
api_hash = config['Config']['API_HASH']
phone_number = config['Config']['PHONE']
password = config['Config']['PASSWORD']


conn = sqlite3.connect(
    'bd/database.db',
    check_same_thread=False
)

cursor = conn.cursor()

chats = [
    'mediasocialmarket',
    'terncrypto_otc',
    'MarketICOBOG'
]

# doubletop - чат, который банит виртуальные аккаунты

counter = 0

data = []


def db_table_val(id: int, chat: str, id_user: int, first_name: str, last_name: str, username: str, date: str, text: str):
    """Добавление записи в БД"""
    cursor.execute(
        'INSERT INTO data (id, chat, id_user, first_name, last_name, username, date, text) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (
            id,
            chat,
            id_user,
            first_name,
            last_name,
            username,
            date,
            text,
        )
    )
    conn.commit()


def search_text(text: str) -> bool:
    if text in data:
        return True
    else:
        return False


def delete_text_from_data():
    while True:
        print(f'До {len(data)}')
        if len(data) < 1001:
            break
        a = data.pop(-1)
        print(f'После {len(data)}')


def get_record(text: str) -> bool:
    """Поиск повторяющейся записи в БД"""
    try:
        sql_select_query = """SELECT * FROM data WHERE text = ?"""
        cursor.execute(sql_select_query, (text,))
        records = cursor.fetchall()
        if len(records) > 0:
            return True
        else:
            return False
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)


def delete_get_record():
    """Удаление лишних записей, начинается после 1000 шт"""
    try:
        while True:
            sql_select_query = """SELECT * FROM data"""
            cursor.execute(sql_select_query)
            records = cursor.fetchall()
            if len(records) > 1000:
                sql_select_query = """DELETE FROM data WHERE id = (SELECT min(id) FROM data)"""
                cursor.execute(sql_select_query)
                conn.commit()
            else:
                break
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)


async def main(array: list) -> None:
    """Обработка чатов, занесение данных в БД, вывод собщений в избранное"""
    global counter
    count = 0
    async with Client("my_account", api_id=api_id, api_hash=api_hash, phone_number=phone_number, password=password) as app:
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
                    # date = dict_message['date']
                    text = dict_message['text']
                    if (('wts' in text.lower() and 'binance' in text.lower()) or ('wtb' in text.lower() and 'binance' in text.lower())) and search_text(text) is False:
                        counter += 1
                        # db_table_val(
                        #     id=counter,
                        #     chat=title_chat,
                        #     id_user=id_user,
                        #     first_name=first_name,
                        #     last_name=last_name,
                        #     username=username,
                        #     date=date,
                        #     text=text
                        # )
                        if text not in data:
                            data.append(text)
                        html_id_user = f'<a href="tg://user?id={id_user}">{id_user}</a>'
                        message = f'Chat: {title_chat}\nId user: {html_id_user}\nFirst name: {first_name}\nLast name: {last_name}\nUsername: {username}\nText: {text}'
                        count += 1
                        await app.send_message("me", message, parse_mode=enums.ParseMode.HTML)
                await asyncio.sleep(3)
        except errors.exceptions.flood_420.FloodWait as wait_err:
            await asyncio.sleep(wait_err.value)
    # print(f'В БД занесено {count} записей, в этом цикле')


while True:
    asyncio.run(main(chats))
    delete_text_from_data()
