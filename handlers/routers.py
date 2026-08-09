from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime, timedelta
from aiogram.fsm.context import FSMContext
from database.requests import set_user, add_reminding
from forms.remindings import RForm
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

router = Router()

active_alarms = {}

async def alarm(bot: Bot, user_id: int, text: str):
    active_alarms[user_id] = True
    while active_alarms.get(user_id, False):
        await bot.send_message(
            chat_id=user_id,
            text=f"⏰**НАПОМИНАНИЕ!!!**\n{text}\n/stop to stop the reminding.",
            parse_mode="Markdown"
        )

@router.message(Command("start"))
async def start(message: Message):
    await set_user(message.from_user.id, message.from_user.username)
    await message.answer(f"Hello {message.from_user.username},\nYour id: {message.from_user.id}\n/reminding to create a reminding.")

@router.message(Command("reminding"))
async def reminding(message: Message, state: FSMContext):
    await message.answer("Comment:")
    await state.set_state(RForm.text)

@router.message(RForm.text, F.text)
async def process_text(message: Message, state: FSMContext):
    await state.update_data(text = message.text)

    await message.answer("Remind at:")
    await state.set_state(RForm.remind_at)

@router.message(RForm.remind_at, F.text)
async def proccess_time(message: Message, state:FSMContext, scheduler: AsyncIOScheduler, bot: Bot):
    user_input = message.text.strip()

    try:
        hours_str, minutes_str = user_input.split(':')
        hours = int(hours_str)
        minutes = int(minutes_str)

        if not (0 <= hours <= 24 and 0 <= minutes <= 59):
            raise ValueError

    except ValueError:
        await message.answer("Invalid Time(Example: 14:29)")
        return

    now = datetime.now()
    target_time = now.replace(hour = hours, minute = minutes, second = 0, microsecond = 0)
    if target_time <= now:
        target_time += timedelta(days=1)

    data = await state.get_data()
    user_id = message.from_user.id
    text = data.get("text")
    time_str = target_time.strftime("%Y-%m-%d %H:%M:%S")

    reminder_id = await add_reminding(
        tg_id=user_id,
        text=text,
        remind_at=time_str
    )

    scheduler.add_job(
        alarm,
        trigger="date",
        run_date = time_str,
        id = f"reminder_{reminder_id}",
        kwargs={
            "bot": bot,
            "user_id": message.from_user.id,
            "text": text
        }
    )

    formatted_time = target_time.strftime("%d.%m.%Y at %H:%M")
    await message.answer(f"Your reminding is set!!!\nWhen: **{formatted_time}**", parse_mode="Markdown")

    await state.clear()

@router.message(Command("stop"))
async def stop_alarm(message: Message):
    user_id = message.from_user.id

    if active_alarms[user_id]:
        active_alarms[user_id] = False
        await message.answer("You stopped the reminding.")
    else:
        await message.answer("No active remindings found.")