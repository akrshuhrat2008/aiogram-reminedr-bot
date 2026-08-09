from aiogram.fsm.state import State, StatesGroup

class RForm(StatesGroup):
    text = State()
    remind_at = State()