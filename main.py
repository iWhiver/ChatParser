import asyncio

from aiotdlib import Client

API_ID = 0
API_HASH = ''
PHONE_NUMBER = ''
BOT_TOKEN = ''

async def main():
    client = Client(
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE_NUMBER
    )

    async with client:
        me = await client.api.get_me()
        print(f"Successfully logged in as {me.json()}")


if __name__ == '__main__':
    asyncio.run(main())