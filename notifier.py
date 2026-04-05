import requests
import os

ZOHO_WEBHOOK = os.getenv("ZOHO_WEBHOOK_URL")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")


def format_message(data):
    train = f"🚆 {data['train_name']} ({data['train_number']})"

    dep = f"{data['from_station']}"
    arr = f"{data['to_station']}"

    dep_time = data.get("departure_time", "")
    arr_time = data.get("arrival_time", "")
    date = data.get("journey_date", "")

    dep_text = f"{date}, {dep_time}"
    arr_text = f"{date}, {arr_time}"

    passengers = []
    for i, p in enumerate(data["passengers"], start=1):
        passengers.append(f"Passenger {i} - {p['status']} ({p['probability']})")

    passenger_text = "\n".join(passengers)

    chart = data["chart_status"]
    pnr = data["pnr"]

    link = f"https://www.confirmtkt.com/pnr-status/{pnr}"

    message = f"""
🚆 **{data['train_name']} ({data['train_number']})**

🟢 Departure  
{dep}  
🕒 {dep_text}

🔴 Arrival  
{arr}  
🕒 {arr_text}

👥 Passenger Status  
{passenger_text}

📊 Chart Status: {chart}

🔖 PNR: {pnr}
🔗 {link}
"""

    return message


def send_to_cliq(data):
    if not ZOHO_WEBHOOK:
        print("Missing Zoho webhook")
        return

    response = requests.post(ZOHO_WEBHOOK, json=data)
    print("Cliq Status:", response.status_code)


def send_to_discord(message):
    if not DISCORD_WEBHOOK:
        print("Missing Discord webhook")
        return

    payload = {
        "content": message
    }

    response = requests.post(DISCORD_WEBHOOK, json=payload)
    print("Discord Status:", response.status_code)


def send_notification(data):
    print("Sending payload:", data)

    # Send to Cliq (existing)
    send_to_cliq(data)

    # Send to Discord (new)
    message = format_message(data)
    send_to_discord(message)