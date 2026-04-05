import os
import json
import re
from scraper import get_pnr_status
from notifier import send_notification

STATE_FILE = "state.json"

# Load PNRs from env
pnr_env = os.getenv("PNR_LIST", "")
PNR_LIST = [pnr.strip() for pnr in pnr_env.split(",") if pnr.strip()]


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# 🔥 Parse structured data from raw text
def parse_pnr_data(text, pnr):

    # Train name & number
    train_match = re.search(r"(\d{5})\s*-\s*([A-Z\s]+)", text)
    train_number = train_match.group(1) if train_match else "N/A"
    train_name = train_match.group(2).strip() if train_match else "Unknown Train"

    # Stations
    route_match = re.search(
        r"([A-Za-z\s]+)\s-\s[A-Z]+,\s([\d:]+).*?\n([A-Za-z\s]+)\s-\s[A-Z]+,\s([\d:]+)",
        text
    )

    from_station = route_match.group(1).strip() if route_match else "Unknown"
    departure_time = route_match.group(2) if route_match else "00:00"

    to_station = route_match.group(3).strip() if route_match else "Unknown"
    arrival_time = route_match.group(4) if route_match else "00:00"

    # Convert to full datetime (basic assumption)
    departure_time = f"2026-04-22 {departure_time}"
    arrival_time = f"2026-04-23 {arrival_time}"

    # Passenger status
    passengers = []
    matches = re.findall(r"(GNWL\s\d+).*?(\d+%)", text)

    for m in matches[:5]:
        passengers.append({
            "status": m[0],
            "probability": m[1]
        })

    if not passengers:
        passengers.append({
            "status": "Not Available",
            "probability": "-"
        })

    # Chart status
    chart_status = "Prepared" if "Chart Prepared" in text else "Not Prepared"

    return {
        "train_name": train_name,
        "train_number": train_number,
        "from_station": from_station,
        "departure_time": departure_time,
        "to_station": to_station,
        "arrival_time": arrival_time,
        "passengers": passengers,
        "chart_status": chart_status,
        "pnr": pnr
    }


def main():

    if not PNR_LIST:
        print("No PNRs configured")
        return

    state = load_state()

    for pnr in PNR_LIST:
        print(f"Checking PNR: {pnr}")

        raw_text = get_pnr_status(pnr)

        structured_data = parse_pnr_data(raw_text, pnr)

        # Compare using raw text (simpler + reliable)
        if pnr not in state or state[pnr] != raw_text:
            print(f"Change detected for {pnr}")

            send_notification(structured_data)

            state[pnr] = raw_text
        else:
            print(f"No change for {pnr}")

    save_state(state)


if __name__ == "__main__":
    main()