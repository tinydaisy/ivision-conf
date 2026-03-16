"""
/api/event — вызывается из мини-аппа (bot.html).
Отправляет сообщение пользователю через Telegram Bot API
и логирует новых пользователей в Google Sheets API (сервисный аккаунт).
"""
import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler
from datetime import datetime, timezone

import gspread
from google.oauth2.service_account import Credentials

BOT_TOKEN    = os.environ["BOT_TOKEN"]
SHEETS_ID    = os.environ.get("GOOGLE_SHEETS_ID", "RXiUPEAmxVdzBTP9tnJ5ddkoBxuhlnHFgsx_nTkBE")
SHEETS_CREDS = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")  # JSON строкой

# Читаем конфиг с текстами сообщений
_cfg_path = os.path.join(os.path.dirname(__file__), "bot_config.json")
with open(_cfg_path) as _f:
    CONFIG = json.load(_f)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_sheet():
    """Открываем лист bot_users через Google Sheets API."""
    creds_dict = json.loads(SHEETS_CREDS)
    creds      = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    gc         = gspread.authorize(creds)
    return gc.open_by_key(SHEETS_ID).worksheet("bot_users")


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


def log_new_user(tg_id, first_name, last_name, username, partner_id):
    """Записываем нового пользователя в Google Sheets (только если ещё не записан)."""
    if not SHEETS_CREDS:
        return
    try:
        sheet = get_sheet()

        # Проверяем — не записан ли уже этот пользователь
        existing = sheet.col_values(2)  # столбец tg_id
        if str(tg_id) in existing:
            return

        partner_username = get_tg_username(partner_id) if partner_id else ""
        sheet.append_row([
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            str(tg_id),
            f"{first_name or ''} {last_name or ''}".strip(),
            username or "",
            str(partner_id) if partner_id else "",
            partner_username
        ])
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
