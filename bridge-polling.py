#!/usr/bin/env python3
"""Claude Code <-> Telegram Bridge (Polling Mode)"""

import os
import json
import subprocess
import threading
import time
import urllib.request
from pathlib import Path

TMUX_SESSION = os.environ.get("TMUX_SESSION", "claude")
CHAT_ID_FILE = os.path.expanduser("~/.claude/telegram_chat_id")
PENDING_FILE = os.path.expanduser("~/.claude/telegram_pending")
HISTORY_FILE = os.path.expanduser("~/.claude/history.jsonl")
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
UPDATE_OFFSET_FILE = os.path.expanduser("~/.claude/telegram_offset")

BOT_COMMANDS = [
    {"command": "clear", "description": "Clear conversation"},
    {"command": "resume", "description": "Resume session (shows picker)"},
    {"command": "continue_", "description": "Continue most recent session"},
    {"command": "loop", "description": "Ralph Loop: /loop <prompt>"},
    {"command": "stop", "description": "Interrupt Claude (Escape)"},
    {"command": "status", "description": "Check tmux status"},
]

BLOCKED_COMMANDS = [
    "/mcp", "/help", "/settings", "/config", "/model", "/compact", "/cost",
    "/doctor", "/init", "/login", "/logout", "/memory", "/permissions",
    "/pr", "/review", "/terminal", "/vim", "/approved-tools", "/listen"
]


def telegram_api(method, data):
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return None
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode() if data else None,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"Telegram API error: {e}")
        return None


def get_updates(offset=None):
    data = {"timeout": 30}
    if offset:
        data["offset"] = offset
    return telegram_api("getUpdates", data)


def setup_bot_commands():
    result = telegram_api("setMyCommands", {"commands": BOT_COMMANDS})
    if result and result.get("ok"):
        print("Bot commands registered")


def send_typing_loop(chat_id):
    while os.path.exists(PENDING_FILE):
        telegram_api("sendChatAction", {"chat_id": chat_id, "action": "typing"})
        time.sleep(4)


def tmux_exists():
    return subprocess.run(["tmux", "has-session", "-t", TMUX_SESSION], capture_output=True).returncode == 0


def tmux_send(text, literal=True):
    cmd = ["tmux", "send-keys", "-t", TMUX_SESSION]
    if literal:
        cmd.append("-l")
    cmd.append(text)
    subprocess.run(cmd)


def tmux_send_enter():
    subprocess.run(["tmux", "send-keys", "-t", TMUX_SESSION, "Enter"])


def tmux_send_escape():
    subprocess.run(["tmux", "send-keys", "-t", TMUX_SESSION, "Escape"])


def get_recent_sessions(limit=5):
    if not os.path.exists(HISTORY_FILE):
        return []
    sessions = []
    try:
        with open(HISTORY_FILE) as f:
            for line in f:
                try:
                    sessions.append(json.loads(line.strip()))
                except:
                    continue
    except:
        return []
    sessions.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return sessions[:limit]


def get_session_id(project_path):
    encoded = project_path.replace("/", "-").lstrip("-")
    for prefix in [f"-{encoded}", encoded]:
        project_dir = Path.home() / ".claude" / "projects" / prefix
        if project_dir.exists():
            jsonls = list(project_dir.glob("*.jsonl"))
            if jsonls:
                return max(jsonls, key=lambda p: p.stat().st_mtime).stem
    return None


def reply(chat_id, text):
    telegram_api("sendMessage", {"chat_id": chat_id, "text": text})


class BotHandler:
    def __init__(self):
        self.offset = self.load_offset()

    def load_offset(self):
        if os.path.exists(UPDATE_OFFSET_FILE):
            try:
                with open(UPDATE_OFFSET_FILE) as f:
                    return int(f.read().strip())
            except:
                pass
        return 0

    def save_offset(self, offset):
        with open(UPDATE_OFFSET_FILE, "w") as f:
            f.write(str(offset))

    def handle_message(self, msg):
        text = msg.get("text", "")
        chat_id = msg.get("chat", {}).get("id")
        msg_id = msg.get("message_id")

        if not text or not chat_id:
            return

        with open(CHAT_ID_FILE, "w") as f:
            f.write(str(chat_id))

        if text.startswith("/"):
            cmd = text.split()[0].lower()

            if cmd == "/status":
                status = "running" if tmux_exists() else "not found"
                reply(chat_id, f"tmux '{TMUX_SESSION}': {status}")
                return

            if cmd == "/stop":
                if tmux_exists():
                    tmux_send_escape()
                if os.path.exists(PENDING_FILE):
                    os.remove(PENDING_FILE)
                reply(chat_id, "Interrupted")
                return

            if cmd == "/clear":
                if not tmux_exists():
                    reply(chat_id, "tmux not found")
                    return
                tmux_send_escape()
                time.sleep(0.2)
                tmux_send("/clear")
                tmux_send_enter()
                reply(chat_id, "Cleared")
                return

            if cmd == "/continue_":
                if not tmux_exists():
                    reply(chat_id, "tmux not found")
                    return
                tmux_send_escape()
                time.sleep(0.2)
                tmux_send("/exit")
                tmux_send_enter()
                time.sleep(0.5)
                tmux_send("claude --continue --dangerously-skip-permissions")
                tmux_send_enter()
                reply(chat_id, "Continuing...")
                return

            if cmd == "/loop":
                if not tmux_exists():
                    reply(chat_id, "tmux not found")
                    return
                parts = text.split(maxsplit=1)
                if len(parts) < 2:
                    reply(chat_id, "Usage: /loop <prompt>")
                    return
                prompt = parts[1].replace('"', '\\"')
                full = f'{prompt} Output <promise>DONE</promise> when complete.'
                with open(PENDING_FILE, "w") as f:
                    f.write(str(int(time.time())))
                threading.Thread(target=send_typing_loop, args=(chat_id,), daemon=True).start()
                tmux_send(f'/ralph-loop:ralph-loop "{full}" --max-iterations 5 --completion-promise "DONE"')
                time.sleep(0.3)
                tmux_send_enter()
                reply(chat_id, "Ralph Loop started (max 5 iterations)")
                return

            if cmd == "/resume":
                sessions = get_recent_sessions()
                if not sessions:
                    reply(chat_id, "No sessions")
                    return
                kb = [[{"text": "Continue most recent", "callback_data": "continue_recent"}]]
                for s in sessions:
                    sid = get_session_id(s.get("project", ""))
                    if sid:
                        kb.append([{"text": s.get("display", "?")[:40] + "...", "callback_data": f"resume:{sid}"}])
                telegram_api("sendMessage", {"chat_id": chat_id, "text": "Select session:", "reply_markup": {"inline_keyboard": kb}})
                return

            if cmd in BLOCKED_COMMANDS:
                reply(chat_id, f"'{cmd}' not supported (interactive)")
                return

        # Regular message
        print(f"[{chat_id}] {text[:50]}...")
        with open(PENDING_FILE, "w") as f:
            f.write(str(int(time.time())))

        if msg_id:
            telegram_api("setMessageReaction", {"chat_id": chat_id, "message_id": msg_id, "reaction": [{"type": "emoji", "emoji": "\u2705"}]})

        if not tmux_exists():
            reply(chat_id, "tmux not found")
            os.remove(PENDING_FILE)
            return

        threading.Thread(target=send_typing_loop, args=(chat_id,), daemon=True).start()
        tmux_send(text)
        tmux_send_enter()

    def handle_callback_query(self, callback_query):
        # For now, just acknowledge the callback
        telegram_api("answerCallbackQuery", {"callback_query_id": callback_query.get("id")})
        # Note: In polling mode, we'd need to handle this differently
        # but for simplicity, this just acknowledges the callback

    def poll_updates(self):
        setup_bot_commands()
        print(f"Bot polling started | tmux: {TMUX_SESSION}")

        while True:
            try:
                result = get_updates(self.offset)
                if not result or not result.get("ok"):
                    time.sleep(5)
                    continue

                updates = result.get("result", [])
                for update in updates:
                    update_id = update.get("update_id", 0)

                    if "message" in update:
                        self.handle_message(update["message"])
                    elif "callback_query" in update:
                        self.handle_callback_query(update["callback_query"])

                    self.offset = update_id + 1
                    self.save_offset(self.offset)

                if not updates:
                    time.sleep(1)

            except KeyboardInterrupt:
                print("\nStopping bot...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)


def main():
    if not BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not set")
        return

    handler = BotHandler()
    handler.poll_updates()


if __name__ == "__main__":
    main()
