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
# STATUS COLOR (Discord)
# -----------------------------
def get_status_color(passengers):
    for p in passengers:
        if "CNF" in p["status"]:
            return 0x2ecc71  # green
        if "RAC" in p["status"]:
            return 0xf1c40f  # yellow
    return 0xe74c3c  # red (WL)


# -----------------------------
# DISCORD EMBED (🔥 PREMIUM)
# -----------------------------
def build_discord_embed(data):
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

    embed = {
        "title": f"🚆 {data['train_name']} ({data['train_number']})",
        "color": get_status_color(data["passengers"]),
        "fields": [
            {
                "name": "🟢 Departure",
                "value": f"{data['from_station']}\n🕒 {data['formatted_departure']}",
                "inline": False
            },
            {
                "name": "🔴 Arrival",
                "value": f"{data['to_station']}\n🕒 {data['formatted_arrival']}",
                "inline": False
            },
            {
                "name": "👥 Passenger Status",
                "value": passenger_text,
                "inline": False
            },
            {
                "name": "📊 Chart Status",
                "value": data["chart_status"],
                "inline": True
            }
        ],
        "footer": {
            "text": f"PNR: {data['pnr']}"
        },
        "url": f"https://www.confirmtkt.com/pnr-status/{data['pnr']}"
    }

    return embed


# -----------------------------
# CLIQ PREMIUM TEXT
# -----------------------------
def format_cliq_message(data):
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

    return f"""
━━━━━━━━━━━━━━━━━━
🚆 *{data['train_name']} ({data['train_number']})*
━━━━━━━━━━━━━━━━━━

🟢 *Departure*
{data['from_station']}
🕒 {data['formatted_departure']}

🔴 *Arrival*
{data['to_station']}
🕒 {data['formatted_arrival']}

👥 *Passenger Status*
{passenger_text}

📊 *Chart Status:* {data['chart_status']}

🔖 PNR: `{data['pnr']}`
🔗 https://www.confirmtkt.com/pnr-status/{data['pnr']}
""".strip()


# -----------------------------
# SENDERS
# -----------------------------
def send_to_cliq(data):
    if not ZOHO_WEBHOOK:
        print("Missing Zoho webhook")
        return

    message = format_cliq_message(data)

    payload = {
        "text": message
    }

    response = requests.post(ZOHO_WEBHOOK, json=payload)
    print("Cliq Status:", response.status_code)


def send_to_discord(data):
    if not DISCORD_WEBHOOK:
        print("Missing Discord webhook")
        return

    embed = build_discord_embed(data)

    payload = {
        "embeds": [embed]
    }

    response = requests.post(DISCORD_WEBHOOK, json=payload)
    print("Discord Status:", response.status_code)


# -----------------------------
# MAIN ENTRY
# -----------------------------
def send_notification(data):
    print("Sending payload:", data)

    data = process_data(data)

    send_to_cliq(data)
    send_to_discord(data)