"""
/api/event — вызывается из мини-аппа (bot.html).
Отправляет сообщение пользователю через Telegram Bot API
и логирует новых пользователей в Telegram-канал.
"""
import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone

BOT_TOKEN   = os.environ["BOT_TOKEN"]
LOG_BOT_TOKEN = os.environ.get("LOG_BOT_TOKEN", "")   # бот с доступом к каналу
LOG_CHAT_ID   = os.environ.get("LOG_CHAT_ID", "")     # id канала для логов

# Читаем конфиг с текстами сообщений (fallback встроен на случай если файл не найден)
_DEFAULT_CONFIG = {
    "conference_name": "iVision Conf",
    "registration_url": "https://ivision.margoforbs.ru/ivision-conf-7",
    "messages": {
        "start":       {"text": "👋 Привет, {name}!\n\nНажми кнопку — откроется {conference_name}.", "button_text": "Открыть {conference_name}"},
        "event_start": {"text": "Добрейшего-богатейшего! Приветствуем вас на событии! Для регистрации нажмите кнопку «Зарегистрироваться»", "button_text": "Зарегистрироваться"},
        "event_reg":   {"text": "Поздравляю! Вы зарегистрированы"}
    }
}
try:
    _cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_config.json")
    with open(_cfg_path) as _f:
        CONFIG = json.load(_f)
except Exception:
    CONFIG = _DEFAULT_CONFIG


def tg_post(token, method, payload):
    url  = f"https://api.telegram.org/bot{token}/{method}"
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


def log_new_user(tg_id, first_name, last_name, username, partner_id):
    """Отправляем данные нового пользователя в Telegram-канал."""
    if not LOG_BOT_TOKEN or not LOG_CHAT_ID:
        return
    try:
        partner_username = get_tg_username(partner_id) if partner_id else ""
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        dt        = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lines = [
            f"🆕 Новый подписчик",
            f"📅 {dt}",
            f"🆔 {tg_id}",
            f"👤 {full_name}" if full_name else None,
            f"📎 @{username}" if username else None,
            f"🤝 Партнёр: {partner_id}" + (f" (@{partner_username})" if partner_username else "") if partner_id else None,
        ]
        text = "\n".join(l for l in lines if l)
        tg_post(LOG_BOT_TOKEN, "sendMessage", {
            "chat_id": LOG_CHAT_ID,
            "text":    text
        })
    except Exception:
        pass


def send_event_message(user_id, event, user_name=""):
    """Отправляем сообщение пользователю по имени события из bot_config.json."""
    msg = CONFIG.get("messages", {}).get(event)
    if not msg:
        return
    conf_name = CONFIG.get("conference_name", "")
    text      = msg["text"].format(name=user_name, conference_name=conf_name)

    if "button_text" in msg:
        btn_text = msg["button_text"].format(conference_name=conf_name)
        reg_url  = CONFIG.get("registration_url", "")
        tg_post(BOT_TOKEN, "sendMessage", {
            "chat_id":      user_id,
            "text":         text,
            "reply_markup": {"inline_keyboard": [[
                {"text": btn_text, "web_app": {"url": reg_url}}
            ]]}
        })
    else:
        tg_post(BOT_TOKEN, "sendMessage", {"chat_id": user_id, "text": text})


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        try:
            data       = json.loads(body)
            user_id    = str(data.get("user_id", "")).strip()
            event      = str(data.get("event", "")).strip()
            first_name = data.get("first_name", "")
            last_name  = data.get("last_name", "")
            username   = data.get("username", "")
            partner_id = data.get("partner_id", "")

            if user_id and event:
                if event == "event_start":
                    log_new_user(user_id, first_name, last_name, username, partner_id)
                send_event_message(user_id, event, first_name or "")
        except Exception:
            pass

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, *args):
        pass
