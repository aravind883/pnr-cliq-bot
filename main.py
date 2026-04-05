import os
import json
from scraper import get_pnr_status, is_valid_pnr_data
from notifier import send_notification

STATE_FILE = "state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}

    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def main():
    pnr_list = os.getenv("PNR_LIST", "")

    if not pnr_list:
        print("No PNRs configured")
        return

    pnrs = [p.strip() for p in pnr_list.split(",") if p.strip()]

    state = load_state()

    for pnr in pnrs:
        print(f"Checking PNR: {pnr}")

        data = get_pnr_status(pnr)

        # ✅ NEW: VALIDATION CHECK
        if not is_valid_pnr_data(data):
            print(f"⛔ Skipping PNR {pnr}: Invalid data (site issue or structure change)")
            continue

        current_status = json.dumps(data["passengers"], sort_keys=True)

        if state.get(pnr) != current_status:
            print(f"Change detected for {pnr}")

            send_notification(data)

            state[pnr] = current_status
        else:
            print(f"No change for {pnr}")

    save_state(state)


if __name__ == "__main__":
    main()