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


def db_table_val(chat: str, id_user: int, first_name: str, last_name: str, username: str, date: str, text: str):
    cursor.execute(
        'INSERT INTO data (chat, id_user, first_name, last_name, username, date, text) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (
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


async def main(array: list) -> None:
    async with Client("my_account", api_id=api_id, api_hash=api_hash, phone_number=phone_number, password=password) \
            as app:
        try:
            for el in array:
                async for message in app.get_chat_history(el, limit=100):
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
                    if ('wts' in text.lower() and 'binance' in text.lower()) or \
                            ('wtb' in text.lower() and 'binance' in text.lower()):
                        db_table_val(
                            chat=title_chat,
                            id_user=id_user,
                            first_name=first_name,
                            last_name=last_name,
                            username=username,
                            date=date,
                            text=text
                        )
                        message = f'Chat: {title_chat}\nFirst name: {first_name}\nLast name: {last_name}' \
                                  f'\nUsername: {username}\nText: {text}'
                        await app.send_message("me", message)
                await asyncio.sleep(3)
        except errors.exceptions.flood_420.FloodWait as wait_err:
            await asyncio.sleep(wait_err.value)

if __name__ == '__main__':
    asyncio.run(main(chats))
