from playwright.sync_api import sync_playwright


def get_pnr_status(pnr):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            url = f"https://www.confirmtkt.com/pnr-status/{pnr}"
            page.goto(url, timeout=60000)

            # Wait for passenger table
            page.wait_for_selector("tbody tr", timeout=20000)

            # -----------------------------
            # TRAIN NAME & NUMBER
            # -----------------------------
            train_el = page.query_selector("p.body-md.font-medium")
            train_text = train_el.inner_text().strip() if train_el else "Unknown Train"

            train_number = ""
            train_name = train_text

            if "-" in train_text:
                parts = train_text.split("-")
                train_number = parts[0].strip()
                train_name = parts[1].strip()

            # -----------------------------
            # FROM / TO STATIONS + TIME
            # -----------------------------
            station_elements = page.query_selector_all("p.body-sm.text-secondary")

            from_station = station_elements[0].inner_text().strip() if len(station_elements) > 0 else "Unknown"
            to_station = station_elements[1].inner_text().strip() if len(station_elements) > 1 else "Unknown"

            time_elements = page.query_selector_all("p.body-md.font-semibold")

            departure_time = time_elements[0].inner_text().strip() if len(time_elements) > 0 else "00:00"
            arrival_time = time_elements[1].inner_text().strip() if len(time_elements) > 1 else "00:00"

            # Convert to datetime string (basic formatting)
            departure_time = f"2026-04-22 {departure_time}"
            arrival_time = f"2026-04-23 {arrival_time}"

            # -----------------------------
            # ✅ PASSENGER STATUS (FIXED)
            # -----------------------------
            rows = page.query_selector_all("tbody tr")

            passengers = []

            for i, row in enumerate(rows, start=1):
                # ONLY CURRENT STATUS COLUMN
                status_el = row.query_selector("td:nth-child(2) p.body-lg")

                if status_el:
                    status = status_el.inner_text().strip()

                    # Try to get probability if exists
                    prob_el = row.query_selector("td:nth-child(2) p.body-xs")
                    probability = prob_el.inner_text().strip() if prob_el else "-"

                    passengers.append({
                        "status": status,
                        "probability": probability
                    })

            # Fallback
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

            # -----------------------------
            # FINAL STRUCTURED DATA
            # -----------------------------
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