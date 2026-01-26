#!/usr/bin/env python3
"""Test script to send message to Telegram"""

import os
import json
import urllib.request

def send_test_message(chat_id, text):
    token = "8584639569:AAF3yQtf5YgUtdeKPMBKLLhdZDBM4L_W5J4"

    # Set up proxy if environment variables are set
    proxy_handler = None
    if os.environ.get('https_proxy'):
        print(f"Using proxy: {os.environ['https_proxy']}")
        proxy_handler = urllib.request.ProxyHandler({'https': os.environ['https_proxy']})
    elif os.environ.get('http_proxy'):
        print(f"Using proxy: {os.environ['http_proxy']}")
        proxy_handler = urllib.request.ProxyHandler({'https': os.environ['http_proxy']})

    if proxy_handler:
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)

    data = {"chat_id": chat_id, "text": text}
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json.dumps(data).encode(),
        {"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read())
            print(f"Message sent: {result}")
            return result.get("ok")
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    chat_id = "940063021"
    test_message = "Test message from bridge test script!"

    if os.environ.get('https_proxy'):
        print(f"Using HTTPS proxy: {os.environ['https_proxy']}")

    success = send_test_message(chat_id, test_message)
    if success:
        print("✅ Test message sent successfully!")
    else:
        print("❌ Failed to send test message")
