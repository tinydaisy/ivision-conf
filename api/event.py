"""
/api/event — вызывается из мини-аппа (bot.html).
Отправляет сообщение пользователю через Telegram Bot API
и логирует новых пользователей в Google Sheets (через Apps Script).
"""
import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone

BOT_TOKEN         = os.environ["BOT_TOKEN"]
SHEETS_WEBHOOK_URL = os.environ.get("SHEETS_WEBHOOK_URL", "")  # Google Apps Script URL

# Читаем конфиг с текстами сообщений
_cfg_path = os.path.join(os.path.dirname(__file__), "bot_config.json")
with open(_cfg_path) as _f:
    CONFIG = json.load(_f)


def tg_post(method, payload):
    """Вызов Telegram Bot API."""
    url  = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=data,
                                   headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def get_tg_username(tg_id):
    """Получаем username пользователя по его Telegram ID."""
    try:
        url  = f"https://api.telegram.org/bot{BOT_TOKEN}/getChat?chat_id={tg_id}"
        resp = urllib.request.urlopen(url, timeout=3).read()
        return json.loads(resp).get("result", {}).get("username", "")
    except Exception:
        return ""


def log_new_user(tg_id, first_name, last_name, username, partner_id):
    """Записываем нового пользователя в Google Sheets через Apps Script."""
    if not SHEETS_WEBHOOK_URL:
        return
    try:
        partner_username = get_tg_username(partner_id) if partner_id else ""
        payload = json.dumps({
            "datetime":            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "tg_id":               str(tg_id),
            "full_name":           f"{first_name or ''} {last_name or ''}".strip(),
            "tg_username":         username or "",
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


def send_event_message(user_id, event, user_name=""):
    """Отправляем сообщение по имени события из bot_config.json."""
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
