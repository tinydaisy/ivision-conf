"""
Telegram webhook — обрабатывает сообщения от пользователей в боте.
- /start         → кнопка «Открыть мини-апп»
- event_start    → приветственное сообщение + кнопка «Зарегистрироваться»
- event_reg      → сообщение «Поздравляю! Вы зарегистрированы»
"""
import os
import json
import asyncio
import urllib.request
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlencode
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

BOT_TOKEN          = os.environ["BOT_TOKEN"]
TMA_URL            = os.environ.get("TMA_URL", "https://ivision-conf.vercel.app")
SHEETS_WEBHOOK_URL = os.environ.get("SHEETS_WEBHOOK_URL", "")

# Читаем конфиг с текстами
_cfg_path = os.path.join(os.path.dirname(__file__), "bot_config.json")
with open(_cfg_path) as _f:
    CONFIG = json.load(_f)

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()


def build_url(base, **params):
    filtered = {k: v for k, v in params.items() if v}
    return f"{base}?{urlencode(filtered)}" if filtered else base


def parse_payload(payload):
    """ref_5725111966_insta → {partner_id, utm_source}"""
    if not payload.startswith("ref_"):
        return {}
    parts  = payload[4:].split("_", 1)
    result = {}
    if parts[0]:
        result["partner_id"] = parts[0]
    if len(parts) > 1 and parts[1]:
        result["utm_source"] = parts[1]
    return result


def tg_post(method, payload):
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data,
                                   headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def get_tg_username(tg_id):
    try:
        url  = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={tg_id}"
        resp = urllib.request.urlopen(url, timeout=3).read()
        return json.loads(resp).get("result", {}).get("username", "")
    except Exception:
        return ""


def log_new_user(user, partner_id=""):
    if not SHEETS_WEBHOOK_URL:
        return
    try:
        partner_username = get_tg_username(partner_id) if partner_id else ""
        payload = json.dumps({
            "datetime":            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "tg_id":               str(user.id),
            "full_name":           f"{user.first_name or ''} {user.last_name or ''}".strip(),
            "tg_username":         user.username or "",
            "partner_tg_id":       str(partner_id) if partner_id else "",
            "partner_tg_username": partner_username
        }).encode()
        req = urllib.request.Request(
            SHEETS_WEBHOOK_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def send_event_message_sync(user_id, event, user_name=""):
    """Отправить сообщение по имени события."""
    msg = CONFIG.get("messages", {}).get(event)
    if not msg:
        return
    conf_name = CONFIG.get("conference_name", "")
    text      = msg["text"].format(name=user_name, conference_name=conf_name)

    if "button_text" in msg:
        btn_text = msg["button_text"].format(conference_name=conf_name)
        reg_url  = CONFIG.get("registration_url", "")
        tg_post("sendMessage", {
            "chat_id":      user_id,
            "text":         text,
            "reply_markup": {"inline_keyboard": [[
                {"text": btn_text, "web_app": {"url": reg_url}}
            ]]}
        })
    else:
        tg_post("sendMessage", {"chat_id": user_id, "text": text})


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    text_parts = message.text.split(maxsplit=1)
    payload    = text_parts[1] if len(text_parts) > 1 else ""
    parsed     = parse_payload(payload)
    partner_id = parsed.get("partner_id", "")
    utm_source = parsed.get("utm_source", "")
    tg_id      = str(message.from_user.id)

    # Логируем нового пользователя
    log_new_user(message.from_user, partner_id)

    tma_url = build_url(TMA_URL + "/bot",
                        new_partner_id=partner_id,
                        utm_source=utm_source,
                        tg_id=tg_id)

    conf_name = CONFIG.get("conference_name", "iVision Conf")
    btn_text  = CONFIG["messages"]["start"]["button_text"].format(conference_name=conf_name)
    text      = CONFIG["messages"]["start"]["text"].format(
        name=message.from_user.first_name or "",
        conference_name=conf_name
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=btn_text, web_app=WebAppInfo(url=tma_url))
    ]])
    await message.answer(text, reply_markup=keyboard)


@dp.message(F.text == "event_start")
async def cmd_event_start(message: types.Message):
    send_event_message_sync(
        message.from_user.id,
        "event_start",
        message.from_user.first_name or ""
    )


@dp.message(F.text == "event_reg")
async def cmd_event_reg(message: types.Message):
    send_event_message_sync(
        message.from_user.id,
        "event_reg",
        message.from_user.first_name or ""
    )


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        async def process():
            update = types.Update.model_validate_json(body)
            await dp.feed_update(bot, update)

        asyncio.run(process())

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, *args):
        pass
