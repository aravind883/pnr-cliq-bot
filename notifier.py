import requests
import os
from datetime import datetime, timedelta

ZOHO_WEBHOOK = os.getenv("ZOHO_WEBHOOK_URL")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")


# -----------------------------
# CORE PROCESSING
# -----------------------------
def format_datetime(date_str, time_str):
    try:
        return datetime.strptime(f"{date_str} {time_str}", "%d %b %Y %H:%M")
    except:
        return None


def format_output(dt):
    if not dt:
        return "⚠️ Date unavailable"
    return dt.strftime("%d %b %Y, %-I:%M %p")


def process_data(data):
    date = data.get("journey_date", "")
    dep_time = data.get("departure_time", "")
    arr_time = data.get("arrival_time", "")

    dep_dt = format_datetime(date, dep_time)
    arr_dt = format_datetime(date, arr_time)

    # Overnight fix
    if dep_dt and arr_dt and arr_dt <= dep_dt:
        arr_dt += timedelta(days=1)

    data["formatted_departure"] = format_output(dep_dt)
    data["formatted_arrival"] = format_output(arr_dt)

    return data


# -----------------------------
# UNIFIED MESSAGE FORMAT
# -----------------------------
def format_message(data, platform="cliq"):
    bold = "**" if platform == "discord" else "*"
    code = "`" if platform == "cliq" else ""

    passengers = []
    for i, p in enumerate(data["passengers"], start=1):
        emoji = "🔴"

        if "CNF" in p["status"]:
            emoji = "🟢"
        elif "RAC" in p["status"]:
            emoji = "🟡"

        line = f"{emoji} Passenger {i} - {p['status']}"
        if p["probability"] and p["probability"] != "-":
            line += f" ({p['probability']})"

        passengers.append(line)

    passenger_text = "\n".join(passengers)

    message = f"""
🚆 {bold}{data['train_name']} ({data['train_number']}){bold}

🟢 {bold}Departure{bold}
{data['from_station']}
🕒 {data['formatted_departure']}

🔴 {bold}Arrival{bold}
{data['to_station']}
🕒 {data['formatted_arrival']}

👥 {bold}Passenger Status{bold}
{passenger_text}

📊 {bold}Chart Status:{bold} {data['chart_status']}

🔖 PNR: {code}{data['pnr']}{code}
🔗 https://www.confirmtkt.com/pnr-status/{data['pnr']}
"""

    return message.strip()


# -----------------------------
# SENDERS
# -----------------------------
def send_to_cliq(message):
    if not ZOHO_WEBHOOK:
        print("Missing Zoho webhook")
        return

    payload = {
        "text": message
    }

    response = requests.post(ZOHO_WEBHOOK, json=payload)
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


# -----------------------------
# MAIN ENTRY
# -----------------------------
def send_notification(data):
    print("Sending payload:", data)

    data = process_data(data)

    cliq_msg = format_message(data, "cliq")
    discord_msg = format_message(data, "discord")

    send_to_cliq(cliq_msg)
    send_to_discord(discord_msg)