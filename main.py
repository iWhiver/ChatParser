import asyncio
from os import getenv
from dotenv import load_dotenv
import sqlite3
from json import loads
from pyrogram import Client, errors
load_dotenv()


BOT_TOKEN = getenv('BOT_TOKEN')
api_id = int(getenv('API_ID'))
api_hash = getenv('API_HASH')
phone_number = getenv('PHONE')
password = getenv('PASSWORD')


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
                async for message in app.get_chat_history(el, limit=10):
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
                    if (('wts' in text.lower() and 'binance' in text.lower()) or ('wtb' in text.lower() and 'binance' in text.lower())) and get_record(text) is False:
                        counter += 1
                        db_table_val(
                            id=counter,
                            chat=title_chat,
                            id_user=id_user,
                            first_name=first_name,
                            last_name=last_name,
                            username=username,
                            date=date,
                            text=text
                        )
                        message = f'Chat: {title_chat}\nFirst name: {first_name}\nLast name: {last_name}\nUsername: {username}\nText: {text}'
                        count += 1
                        await app.send_message("me", message)
                await asyncio.sleep(3)
        except errors.exceptions.flood_420.FloodWait as wait_err:
            await asyncio.sleep(wait_err.value)
    print(f'В БД занесено {count} записей, в этом цикле')


while True:
    asyncio.run(main(chats))
    delete_get_record()
