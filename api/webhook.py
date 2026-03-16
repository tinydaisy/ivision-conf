"""
Telegram webhook — синхронный обработчик без aiogram async.
- /start         → кнопка «Открыть мини-апп»
- event_start    → приветственное сообщение + кнопка «Зарегистрироваться»
- event_reg      → сообщение «Поздравляю! Вы зарегистрированы»
"""
import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlencode
from datetime import datetime, timezone

BOT_TOKEN     = os.environ["BOT_TOKEN"]
TMA_URL       = os.environ.get("TMA_URL", "https://ivision-conf.vercel.app")
LOG_BOT_TOKEN = os.environ.get("LOG_BOT_TOKEN", "")
LOG_CHAT_ID   = os.environ.get("LOG_CHAT_ID", "")

CONFIG = {
    "conference_name": "iVision Conf",
    "registration_url": "https://ivision.margoforbs.ru/ivision-conf-7",
    "messages": {
        "start":       {"text": "👋 Привет, {name}!\n\nНажми кнопку — откроется {conference_name}.", "button_text": "Открыть {conference_name}"},
        "event_start": {"text": "Добрейшего-богатейшего! Приветствуем вас на событии! Для регистрации нажмите кнопку «Зарегистрироваться»", "button_text": "Зарегистрироваться"},
        "event_reg":   {"text": "Поздравляю! Вы зарегистрированы"}
    }
}
try:
    _cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_config.json")
    with open(_cfg) as f:
        CONFIG = json.load(f)
except Exception:
    pass


def tg_post(token, method, payload):
    url  = f"https://api.telegram.org/bot{token}/{method}"
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data,
                                   headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def get_username(tg_id):
    try:
        url  = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={tg_id}"
        resp = urllib.request.urlopen(url, timeout=3).read()
        return json.loads(resp).get("result", {}).get("username", "")
    except Exception:
        return ""


def send_message(user_id, event, name=""):
    msg = CONFIG["messages"].get(event)
    if not msg:
        return
    conf = CONFIG.get("conference_name", "")
    text = msg["text"].format(name=name, conference_name=conf)

    if "button_text" in msg:
        btn = msg["button_text"].format(conference_name=conf)
        url = CONFIG.get("registration_url", "")
        tg_post(BOT_TOKEN, "sendMessage", {
            "chat_id": user_id, "text": text,
            "reply_markup": {"inline_keyboard": [[
                {"text": btn, "web_app": {"url": url}}
            ]]}
        })
    else:
        tg_post(BOT_TOKEN, "sendMessage", {"chat_id": user_id, "text": text})


def log_user(user_id, first_name, last_name, username, partner_id):
    if not LOG_BOT_TOKEN or not LOG_CHAT_ID:
        return
    try:
        partner_uname = get_username(partner_id) if partner_id else ""
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        dt = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lines = [
            "🆕 Новый подписчик", f"📅 {dt}", f"🆔 {user_id}",
            f"👤 {full_name}" if full_name else None,
            f"📎 @{username}" if username else None,
            (f"🤝 Партнёр: {partner_id}" + (f" (@{partner_uname})" if partner_uname else "")) if partner_id else None,
        ]
        tg_post(LOG_BOT_TOKEN, "sendMessage", {
            "chat_id": LOG_CHAT_ID,
            "text":    "\n".join(l for l in lines if l)
        })
    except Exception:
        pass


def parse_start_payload(payload):
    """ref_5725111966_insta → (partner_id, utm_source)"""
    if not payload.startswith("ref_"):
        return "", ""
    parts = payload[4:].split("_", 1)
    return parts[0], (parts[1] if len(parts) > 1 else "")


def handle_update(data):
    msg = data.get("message") or data.get("edited_message")
    if not msg:
        return

    user    = msg.get("from", {})
    user_id = user.get("id")
    text    = (msg.get("text") or "").strip()

    if not user_id or not text:
        return

    first_name = user.get("first_name", "")
    last_name  = user.get("last_name", "")
    username   = user.get("username", "")

    # /start [payload]
    if text.startswith("/start"):
        parts      = text.split(maxsplit=1)
        payload    = parts[1] if len(parts) > 1 else ""
        partner_id, utm = parse_start_payload(payload)

        log_user(user_id, first_name, last_name, username, partner_id)

        tma_url = TMA_URL + "/bot"
        params  = {k: v for k, v in [("new_partner_id", partner_id), ("utm_source", utm), ("tg_id", str(user_id))] if v}
        if params:
            tma_url += "?" + urlencode(params)

        conf = CONFIG.get("conference_name", "iVision Conf")
        btn  = CONFIG["messages"]["start"]["button_text"].format(conference_name=conf)
        txt  = CONFIG["messages"]["start"]["text"].format(name=first_name, conference_name=conf)
        tg_post(BOT_TOKEN, "sendMessage", {
            "chat_id": user_id, "text": txt,
            "reply_markup": {"inline_keyboard": [[
                {"text": btn, "web_app": {"url": tma_url}}
            ]]}
        })
        return

    if text == "event_start":
        send_message(user_id, "event_start", first_name)
        return

    if text == "event_reg":
        send_message(user_id, "event_reg", first_name)
        return


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        try:
            handle_update(json.loads(body))
        except Exception:
            pass

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def log_message(self, *args):
        pass
