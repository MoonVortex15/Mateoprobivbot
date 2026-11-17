from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.osint_service import lookup_username

router = Router(name="osint")


@router.message(Command("username"))
async def cmd_username(message: Message) -> None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Использование: <code>/username ник</code>")
        return

    username = parts[1].strip().lstrip("@")
    await message.answer(f"🔎 Ищу <b>{username}</b>...")
    result = await lookup_username(username)
    await message.answer(result)
