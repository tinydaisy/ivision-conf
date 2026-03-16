import os
import asyncio
import urllib.request
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlencode

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN        = os.environ["BOT_TOKEN"]
LANDING_URL      = os.environ["LANDING_URL"]
TMA_URL          = os.environ.get("TMA_URL", "https://ivision-conf.vercel.app")
CONFERENCE_NAME  = os.environ.get("CONFERENCE_NAME", "iVision Conf")
SALEBOT_API_KEY  = os.environ.get("SALEBOT_API_KEY", "315a5e0842886f038831a5a29fbb9aa2")
SALEBOT_HOOK_URL = f"https://chatter.salebot.pro/api/{SALEBOT_API_KEY}/message"

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()


def build_url(base: str, **params) -> str:
    filtered = {k: v for k, v in params.items() if v}
    return f"{base}?{urlencode(filtered)}" if filtered else base


def parse_payload(payload: str) -> dict:
    """
    /start ref_5725111966_insta
    → {"new_partner_id": "5725111966", "utm_source": "insta"}
    """
    if not payload.startswith("ref_"):
        return {}
    parts = payload[4:].split("_", 1)
    result = {}
    if parts[0]:
        result["new_partner_id"] = parts[0]
    if len(parts) > 1 and parts[1]:
        result["utm_source"] = parts[1]
    return result


@dp.message(CommandStart())
async def start(message: types.Message):
    text_parts = message.text.split(maxsplit=1)
    payload    = text_parts[1] if len(text_parts) > 1 else ""
    utm_params = parse_payload(payload)
    tg_id      = str(message.from_user.id)

    # TMA открывается как мини-апп и сразу редиректит на лендинг с UTM
    tma_url = build_url(
        TMA_URL,
        new_partner_id=utm_params.get("new_partner_id", ""),
        utm_source=utm_params.get("utm_source", ""),
        tg_id=tg_id
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=f"Открыть {CONFERENCE_NAME}",
            web_app=WebAppInfo(url=tma_url)
        )
    ]])
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Нажми кнопку — откроется {CONFERENCE_NAME}.",
        reply_markup=keyboard
    )


def forward_to_salebot(body: bytes):
    """Проксируем апдейт в Salebot — он обрабатывает кодовые слова и всё остальное."""
    try:
        req = urllib.request.Request(
            SALEBOT_HOOK_URL,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass  # не блокируем ответ Telegram если Salebot недоступен


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        # 1. Наш бот обрабатывает /start (открывает мини-апп)
        async def process():
            update = types.Update.model_validate_json(body)
            await dp.feed_update(bot, update)

        asyncio.run(process())

        # 2. Все апдейты проксируются в Salebot (кодовые слова, диалоги и т.д.)
        forward_to_salebot(body)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, *args):
        pass
