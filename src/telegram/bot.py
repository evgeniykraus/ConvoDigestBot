import io
import json
from aiogram.types import BufferedInputFile, BotCommand
from src.config.config import load_config
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from src.telegram.telethon_client import get_list_chats

# Описание команд для меню Telegram
BOT_COMMANDS = [
    BotCommand(command="start", description="Приветствие и краткая справка"),
    BotCommand(command="help", description="Подробная справка по боту"),
    BotCommand(command="list_chats_json", description="Получить список чатов в JSON"),
]

async def run_bot():
    bot = Bot(token=load_config().get('BOT_TOKEN'))
    dp = Dispatcher()
    config = load_config()
    OWNER_ID = config.get('TELEGRAM_OWNER_ID')

    def is_owner(message: types.Message) -> bool:
        return message.from_user.id == OWNER_ID

    # Устанавливаем команды для Telegram-клиента
    await bot.set_my_commands(BOT_COMMANDS)

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        if not is_owner(message):
            return
        await message.answer(
            "Привет! Я бот для генерации еженедельных дайджестов чата. Просто жди отчётов!\n/help — помощь.")

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message):
        if not is_owner(message):
            return
        await message.answer(
            "Я автоматически собираю сообщения за неделю, генерирую отчёт и отправляю его в этот чат.\n\nДоступные команды:\n/start — приветствие\n/help — справка\n/auth — авторизация Telethon\n/list_chats_json — список чатов в JSON")

    @dp.message(Command("list_chats_json"))
    async def cmd_list_chats_json(message: types.Message):
        if not is_owner(message):
            return
        temp_message = await message.answer("🔄 Генерирую отчёт по чатам, подожди пару секунд...")

        # Получаем список чатов
        chats = await get_list_chats()
        json_text = json.dumps(chats, ensure_ascii=False, indent=2)

        # Создаём буфер для JSON-файла
        buffer = io.BytesIO(json_text.encode("utf-8"))
        buffer.name = "chat_list.json"
        await message.answer_document(BufferedInputFile(buffer.read(), filename=buffer.name))

        await temp_message.delete()

    await dp.start_polling(bot)
