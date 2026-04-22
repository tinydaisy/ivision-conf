"""
FastAPI-обёртка для запуска на Beget VPS.
Порт: 8002
"""
import os
import json
import sys

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(__file__))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    body = await request.body()
    try:
        from webhook import handle_update
        handle_update(json.loads(body))
    except Exception:
        pass
    return {"ok": True}


@app.post("/api/event")
async def event_endpoint(request: Request):
    body = await request.body()
    try:
        import event as ev
        data = json.loads(body)
        user_id    = str(data.get("user_id", "")).strip()
        event_name = str(data.get("event", "")).strip()
        first_name = data.get("first_name", "")
        last_name  = data.get("last_name", "")
        username   = data.get("username", "")
        partner_id = data.get("partner_id", "")

        if user_id and event_name:
            if event_name == "event_start":
                ev.log_new_user(user_id, first_name, last_name, username, partner_id)
            ev.send_event_message(user_id, event_name, first_name or "")
    except Exception:
        pass
    return {"ok": True}


@app.options("/api/event")
async def event_options():
    return Response(status_code=200)


@app.get("/health")
async def health():
    return {"status": "ok"}
