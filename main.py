import asyncio
import logging
import sys
from multiprocessing import Process

from src.scheduler.scheduler import schedule_weekly_job
from src.telegram.bot import run_bot

def main():
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
            print("Unknown mode. Use 'bot' or 'scheduler'.")
            return
    # По умолчанию запускать оба процесса
    p1 = Process(target=lambda: asyncio.run(run_bot()))
    p2 = Process(target=lambda: asyncio.run(schedule_weekly_job()))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
    main()
