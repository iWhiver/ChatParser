import uvloop
import asyncio
import configparser
from json import loads
from pyrogram import Client, errors, enums

config = configparser.ConfigParser()
config.read(".ini")

api_id = config['Config']['API_ID']
api_hash = config['Config']['API_HASH']
phone_number = config['Config']['PHONE']
password = config['Config']['PASSWORD']

chats = [
    'mediasocialmarket',
    'terncrypto_otc',
    'MarketICOBOG'
]

MESSAGE_LIMIT = 50
SEARCH_COIN = 'Binance'.lower()
WTS = True
WTB = False
data = []


async def main():
    app = Client("my_account", api_id=api_id, api_hash=api_hash,
                 phone_number=phone_number, password=password)

    async with app:
        await logic(app)


def create_a_message(dict_message, text):
    html_id_user = f"t.me/user?id={dict_message['from_user']['id']}"
    message = f"Chat: {dict_message['chat']['title']}\n" \
              f"Id user: {html_id_user}\n" \
              f"Username: {dict_message['from_user']['username']}\n" \
              f"Text: {text}"
    return message


async def logic(app: Client) -> None:
    try:
        for chat in chats:
            async for message in app.get_chat_history(chat, limit=MESSAGE_LIMIT):
                dict_message = loads(str(message))
                # date = dict_message['date']
                text = dict_message['text'].lower()
                if ((('wts' in text and WTS) and SEARCH_COIN in text) or
                        ('wtb' in text and WTB) and SEARCH_COIN in text):

                    if text not in data:
                        data.append(text)

                    message = create_a_message(dict_message, text)
                    print(message)
                    print("=========================================")
                    await app.send_message("me", message, parse_mode=enums.ParseMode.HTML)
            await asyncio.sleep(10)

    except errors.exceptions.flood_420.FloodWait as wait_err:
        print('wait after flood')
        await asyncio.sleep(wait_err.value)

    # await asyncio.sleep(60)


uvloop.install()
asyncio.run(main())
