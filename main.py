import os
from os import getenv
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers.routers import router
from database.models import init_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

scheduler = AsyncIOScheduler()

async def handle_health(request):
    return web.Response(text="OK", status=200)

async def start_health_check():
    app = web.Application()
    app.router.add_get("/", handle_health)
    app.router.add_get("/health", handle_health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await start_health_check()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    await init_db()
    scheduler.start()
    dp.include_router(router)
    dp["scheduler"] = scheduler
    print("Starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())