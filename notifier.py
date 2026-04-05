import requests
import os

ZOHO_WEBHOOK = os.getenv("ZOHO_WEBHOOK_URL")

def send_notification(data):
    if not ZOHO_WEBHOOK:
        print("Missing ZOHO_WEBHOOK_URL")
        return

    print("Sending payload:", data)

    try:
        response = requests.post(ZOHO_WEBHOOK, json=data, timeout=10)
        print("Status Code:", response.status_code)
        print("Response:", response.text)
    except Exception as e:
        print("Error sending notification:", str(e))