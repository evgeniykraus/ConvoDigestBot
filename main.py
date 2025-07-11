import asyncio
import logging

from src.scheduler.scheduler import schedule_weekly_job


def main():
    asyncio.run(schedule_weekly_job())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
    main()
