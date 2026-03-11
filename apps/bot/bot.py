import asyncio
import os
from urllib.parse import urlencode
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

BOT_TOKEN       = os.getenv("BOT_TOKEN")
LANDING_URL     = os.getenv("LANDING_URL")
CONFERENCE_NAME = os.getenv("CONFERENCE_NAME", "iVision Conf")

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()


def build_url(base: str, **params) -> str:
    """Добавляет непустые параметры к URL."""
    filtered = {k: v for k, v in params.items() if v}
    return f"{base}?{urlencode(filtered)}" if filtered else base


def parse_payload(payload: str) -> dict:
    """
    Разбирает start-параметр вида: ref_5725111966_insta
    → {"new_partner_id": "5725111966", "utm_source": "insta"}
    """
    if not payload.startswith("ref_"):
        return {}
    rest = payload[4:]  # отрезаем "ref_"
    parts = rest.split("_", 1)
    result = {}
    if parts[0]:
        result["new_partner_id"] = parts[0]
    if len(parts) > 1 and parts[1]:
        result["utm_source"] = parts[1]
    return result


@dp.message(CommandStart())
async def start(message: types.Message):
    # Извлекаем payload из команды /start <payload>
    text_parts = message.text.split(maxsplit=1)
    payload = text_parts[1] if len(text_parts) > 1 else ""

    utm_params = parse_payload(payload)
    tg_id = str(message.from_user.id)

    url = build_url(LANDING_URL, tg_id=tg_id, **utm_params)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=f"Открыть {CONFERENCE_NAME}", url=url)
    ]])
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Нажми кнопку ниже, чтобы перейти на {CONFERENCE_NAME}.",
        reply_markup=keyboard
    )


async def main():
    print(f"Бот запущен: {CONFERENCE_NAME}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
