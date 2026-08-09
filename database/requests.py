from database.models import async_session, User, Reminder
from sqlalchemy import select

async def set_user(tg_id: int, username: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, username = username))
            session.commit()

async def add_reminding(tg_id: int, text: str, remind_at: str):
    async with async_session() as session:
        session.add(Reminder(user_id = tg_id, comment = text, remind_at = remind_at))
        session.commit()

async def get_user_remindings(tg_id: int):
    async with async_session() as session:
        result = session.scalars(select(Reminder).where(Reminder.user_id == tg_id))
        return result.all()