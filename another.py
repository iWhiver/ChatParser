import asyncio
from pyrogram import Client

api_id = 0
api_hash = ""
phone_number = '+7999999999'
password = ''


async def main():
    async with Client("my_account", api_id=api_id, api_hash=api_hash, phone_number=phone_number, password=password) as app:
        await app.send_message("me", "Greetings from **Pyrogram**!")
        print('Message sent')


asyncio.run(main())

if __name__ == '__main__':
    asyncio.run(main())