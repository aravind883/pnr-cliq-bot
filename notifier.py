import requests
import os

ZOHO_WEBHOOK = os.getenv("ZOHO_WEBHOOK_URL")

def send_notification(data):
    requests.post(ZOHO_WEBHOOK, json=data)