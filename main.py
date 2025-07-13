import asyncio
import logging
import sys

from src.config.config import load_config
from src.scheduler.scheduler import schedule_weekly_job
from src.telegram.bot import run_bot

config = load_config()
MODE = config['MODE']

async def main():
    # Если явно указан режим
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == 'bot':
            asyncio.run(run_bot())
            return
        elif mode == 'scheduler':
            asyncio.run(schedule_weekly_job())
            return
        else:
            logging.warning("Неизвестный режим. Используйте 'bot' или 'scheduler'.")
            return

    await asyncio.gather(
        run_bot(),
        schedule_weekly_job()
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
    asyncio.run(main())
