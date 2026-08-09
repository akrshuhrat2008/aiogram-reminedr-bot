from os import getenv
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers.routers import router
from database.models import init_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

scheduler = AsyncIOScheduler()

async def main():
    await init_db()
    scheduler.start()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    dp["scheduler"] = scheduler
    print("Starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())