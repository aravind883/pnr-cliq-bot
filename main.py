import os
import json
from scraper import get_pnr_status
from notifier import send_notification

STATE_FILE = "state.json"

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


def main():

    if not PNR_LIST:
        print("No PNRs configured")
        return

    state = load_state()

    for pnr in PNR_LIST:
        print(f"Checking PNR: {pnr}")

        data = get_pnr_status(pnr)

        # Compare using serialized data
        data_string = json.dumps(data, sort_keys=True)

        if pnr not in state or state[pnr] != data_string:
            print(f"Change detected for {pnr}")

            send_notification(data)

            state[pnr] = data_string
        else:
            print(f"No change for {pnr}")

    save_state(state)


if __name__ == "__main__":
    main()