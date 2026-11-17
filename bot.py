import asyncio
import json
import logging
import time
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings
from handlers import osint, start

STATE_FILE = Path("state.json")
# 5 часов 30 минут — с запасом под 6-часовой лимит job в GitHub Actions
RUN_DURATION_SECONDS = 5 * 3600 + 30 * 60


def load_offset() -> int:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            return int(data.get("offset", 0))
        except (json.JSONDecodeError, ValueError):
            logging.warning("state.json битый, начинаем с 0")
    return 0


def save_offset(offset: int) -> None:
    STATE_FILE.write_text(
        json.dumps({"offset": offset}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


async def run_bot() -> None:
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_routers(start.router, osint.router)

    offset = load_offset()
    logging.info("Старт с offset=%s, работаю %s сек", offset, RUN_DURATION_SECONDS)

    allowed_updates = dp.resolve_used_update_types()
    deadline = time.monotonic() + RUN_DURATION_SECONDS

    try:
        while time.monotonic() < deadline:
            try:
                updates = await bot.get_updates(
                    offset=offset,
                    timeout=30,
                    allowed_updates=allowed_updates,
                )
                for update in updates:
                    try:
                        await dp.feed_update(bot, update)
                    except Exception:
                        logging.exception("Ошибка обработки update %s", update.update_id)
                    offset = update.update_id + 1
                    save_offset(offset)
            except asyncio.CancelledError:
                raise
            except Exception:
                logging.exception("Ошибка polling, пауза 5с")
                await asyncio.sleep(5)
    finally:
        await bot.session.close()
        logging.info("Остановлен на offset=%s", offset)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
