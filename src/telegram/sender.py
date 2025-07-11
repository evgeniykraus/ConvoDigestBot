"""
Модуль для отправки итогового отчёта в Telegram-чат через aiogram (Bot API).
"""
import html
import os
import asyncio
from aiogram import Bot
from aiogram.enums import ParseMode
from datetime import datetime

from src.config.config import get_config

config = get_config()
BOT_TOKEN = config['BOT_TOKEN']


def escape_html(text: str) -> str:
    return html.escape(text)


def format_report(report_json: dict) -> str:
    parts = []

    # Шапка с датой
    today = datetime.now().strftime('%d.%m.%Y')
    parts.append(f"<b>💬 Итоги чата за неделю — {today}</b>\n")

    # Важное обсуждение
    if report_json.get('main_fragments'):
        parts.append("📊 <b>Что обсуждали активнее всего:</b>")
        for i, item in enumerate(report_json['main_fragments'], start=1):
            parts.append(f"{i}. {escape_html(item)}")
        parts.append("")

    # Факапы и взбесившее
    if report_json.get('failures_and_rage'):
        parts.append("💥 <b>О наболевшем:</b>")
        for i, item in enumerate(report_json['failures_and_rage'], start=1):
            parts.append(f"{i}. {escape_html(item)}")
        parts.append("")

    # Темы на следующую встречу
    if report_json.get('topics_to_discuss'):
        parts.append("🧨 <b>Темы для нытинга:</b>")
        for i, item in enumerate(report_json['topics_to_discuss'], start=1):
            parts.append(f"{i}. {escape_html(item)}")
        parts.append("")

    # Хэштэг
    parts.append("#нытинг\n")

    return '\n'.join(parts)


async def send_report_async(report_json: dict, chat_id: str):
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(chat_id, format_report(report_json), parse_mode=ParseMode.HTML)
    finally:
        await bot.session.close()


def send_report(report_json: dict, chat_id: str):
    """
    Отправляет текст отчёта в указанный чат через Telegram Bot API.
    """
    asyncio.run(send_report_async(report_json, chat_id))
