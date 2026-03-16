import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlencode

SALEBOT_API_KEY = os.environ.get("SALEBOT_API_KEY", "315a5e0842886f038831a5a29fbb9aa2")


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        try:
            data    = json.loads(body)
            user_id = str(data.get("user_id", "")).strip()
            event   = str(data.get("event", "event_start")).strip()

            if user_id and SALEBOT_API_KEY:
                url     = f"https://chatter.salebot.pro/api/{SALEBOT_API_KEY}/callback"
                payload = urlencode({"client_id": user_id, "message": event}).encode()
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    method="POST"
                )
                urllib.request.urlopen(req, timeout=5)
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
