from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="start")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 Привет! Я OSINT-бот.\n\n"
        "Команды:\n"
        "/help — справка\n"
        "/ping — проверка\n"
        "/username ник — тестовый поиск"
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "📚 <b>Команды:</b>\n"
        "/start — приветствие\n"
        "/help — справка\n"
        "/ping — проверка\n"
        "/username &lt;ник&gt; — тестовый OSINT\n\n"
        "Скоро: email, IP, домены."
    )


@router.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    await message.answer("🏓 Pong!")
