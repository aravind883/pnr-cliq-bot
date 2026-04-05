import requests
import os

ZOHO_WEBHOOK = os.getenv("ZOHO_WEBHOOK_URL")

def send_notification(source, title, message, severity="info"):
    if not ZOHO_WEBHOOK:
        print("Missing ZOHO_WEBHOOK_URL")
        return

    payload = {
        "source": source,
        "title": title,
        "message": message,
        "severity": severity
    }

    try:
        response = requests.post(ZOHO_WEBHOOK, json=payload, timeout=10)
        print("Notification sent:", response.status_code)
    except Exception as e:
        print("Error sending notification:", str(e))