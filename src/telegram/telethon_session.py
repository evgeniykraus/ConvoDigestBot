import asyncio
from telethon import TelegramClient
from src.config.config import load_config

config = load_config()
API_ID = int(config['TELEGRAM_API_ID'])
API_HASH = config['TELEGRAM_API_HASH']
PHONE = config['TELEGRAM_PHONE']
SESSION_NAME = config['TELEGRAM_SESSION_NAME']

async def create_telethon_session():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        print("[Telethon] Необходима авторизация. Введите код, который придёт в Telegram...")
        await client.start(phone=PHONE)
        print("[Telethon] Авторизация завершена!")
    else:
        print("[Telethon] Уже авторизован.")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(create_telethon_session()) 