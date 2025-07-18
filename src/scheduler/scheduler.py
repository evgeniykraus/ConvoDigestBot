"""
Модуль для запуска всего пайплайна раз в неделю через APScheduler.
"""
import asyncio
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from src.config.config import load_config
from src.llm.client import summarize
from src.telegram.sender import send_report
from src.telegram.telethon_client import get_messages

config = load_config()
CHAT_ID = config['TELEGRAM_CHAT_ID']
TELEGRAM_DIST_CHAT_ID = config['TELEGRAM_DIST_CHAT_ID']
DAY_OFFSET = config['DAY_OFFSET']


async def pipeline(chat_id: str = CHAT_ID):
    """Запускает пайплайн для генерации и отправки отчёта."""
    logging.info('Старт пайплайна...')
    try:
        messages = await get_messages(chat_id)
        logging.info(f'Загружено сообщений: {len(messages)} из чата с ID: {chat_id}')
        logging.info('Началась обработка сообщений через RAG...')
        report = await summarize(messages)
        await send_report(report, TELEGRAM_DIST_CHAT_ID)
        logging.info('Отчёт успешно отправлен!')
    except Exception as e:
        logging.error(f'Ошибка в пайплайне: {str(e)}', exc_info=True)
        raise


async def schedule_weekly_job(chat_id: str = CHAT_ID):
    """Запускает асинхронный планировщик для еженедельного отчёта и сразу выполняет задачу."""
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))
    scheduler.add_job(pipeline, 'cron', day_of_week='sun', hour=18, minute=0, args=[chat_id])
    logging.info('Планировщик запущен. Выполняем задачу немедленно...')
    # 👇 Выполняем задачу сразу
    await pipeline(chat_id)

    scheduler.start()
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        logging.info('Планировщик остановлен.')
        scheduler.shutdown()
