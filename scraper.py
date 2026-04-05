from playwright.sync_api import sync_playwright


def get_pnr_status(pnr):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            url = f"https://www.confirmtkt.com/pnr-status/{pnr}"
            page.goto(url, timeout=60000)

            page.wait_for_selector("tbody tr", timeout=20000)

            # -----------------------------
            # TRAIN NAME (FIXED)
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
            # STATIONS + RAW TEXT
            # -----------------------------
            route_blocks = page.locator("p").all_text_contents()

            from_station = ""
            to_station = ""
            departure_time = ""
            arrival_time = ""

            for text in route_blocks:
                if "-" in text and "," in text:
                    if not from_station:
                        from_station = text.strip()
                    elif not to_station:
                        to_station = text.strip()

                # Extract time
                if ":" in text and len(text.strip()) <= 5:
                    if not departure_time:
                        departure_time = text.strip()
                    elif not arrival_time:
                        arrival_time = text.strip()

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
                "departure_time": departure_time,   # ONLY TIME
                "to_station": to_station,
                "arrival_time": arrival_time,       # ONLY TIME
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
            "passengers": [{
                "status": f"Error: {str(e)}",
                "probability": "-"
            }],
            "chart_status": "Unknown",
            "pnr": pnr
        }