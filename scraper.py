from playwright.sync_api import sync_playwright
import re
from datetime import datetime


def get_pnr_status(pnr):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            url = f"https://www.confirmtkt.com/pnr-status/{pnr}"
            page.goto(url, timeout=60000)

            page.wait_for_selector("tbody tr", timeout=20000)

            # -----------------------------
            # TRAIN NAME
            # -----------------------------
            train_el = page.locator("text=/\\d{5} -/").first
            train_text = train_el.inner_text().strip() if train_el else "Unknown Train"

            train_number = ""
            train_name = train_text

            if "-" in train_text:
                parts = train_text.split("-")
                train_number = parts[0].strip()
                train_name = parts[1].strip()

            # -----------------------------
            # ROUTE + TIME
            # -----------------------------
            route_elements = page.locator("p.body-sm").all_text_contents()

            from_station = "Unknown"
            to_station = "Unknown"
            departure_time = ""
            arrival_time = ""

            route_data = []

            for text in route_elements:
                if "-" in text and "," in text:
                    route_data.append(text.strip())

            if len(route_data) >= 2:
                from_parts = route_data[0].split(",")
                to_parts = route_data[1].split(",")

                from_station = from_parts[0].strip()
                departure_time = from_parts[1].strip() if len(from_parts) > 1 else ""

                to_station = to_parts[0].strip()
                arrival_time = to_parts[1].strip() if len(to_parts) > 1 else ""

            # -----------------------------
            # DATE WITH YEAR (FIXED)
            # -----------------------------
            full_text = page.inner_text("body")

            date_match = re.search(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s(\d{1,2}\s\w+)", full_text)

            journey_date = "N/A"

            if date_match:
                day_month = date_match.group(2)   # "22 Apr"
                current_year = datetime.now().year
                journey_date = f"{day_month} {current_year}"  # "22 Apr 2026"

            # -----------------------------
            # PASSENGERS
            # -----------------------------
            rows = page.query_selector_all("tbody tr")

            passengers = []

            for i, row in enumerate(rows, start=1):
                status_el = row.query_selector("td:nth-child(2) p.body-lg")

                if status_el:
                    status = status_el.inner_text().strip()

                    prob_el = row.query_selector("td:nth-child(2) p.body-xs")
                    probability = prob_el.inner_text().strip() if prob_el else "-"

                    passengers.append({
                        "status": status,
                        "probability": probability
                    })

            if not passengers:
                passengers.append({
                    "status": "Not Available",
                    "probability": "-"
                })

            # -----------------------------
            # CHART STATUS
            # -----------------------------
            chart_status = "Prepared"
            if page.locator("text=Chart not prepared").count() > 0:
                chart_status = "Not Prepared"

            browser.close()

            return {
                "train_name": train_name,
                "train_number": train_number,
                "from_station": from_station,
                "departure_time": departure_time,
                "to_station": to_station,
                "arrival_time": arrival_time,
                "journey_date": journey_date,   # ✅ now includes year
                "passengers": passengers,
                "chart_status": chart_status,
                "pnr": pnr
            }

    except Exception as e:
        return {
            "train_name": "Error",
            "train_number": "",
            "from_station": "",
            "departure_time": "",
            "to_station": "",
            "arrival_time": "",
            "journey_date": "",
            "passengers": [{
                "status": f"Error: {str(e)}",
                "probability": "-"
            }],
            "chart_status": "Unknown",
            "pnr": pnr
        }