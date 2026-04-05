from playwright.sync_api import sync_playwright

def get_pnr_status(pnr):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            url = f"https://www.confirmtkt.com/pnr-status/{pnr}"
            page.goto(url, timeout=60000)

            page.wait_for_timeout(5000)

            content = page.inner_text("body")

            browser.close()

            return content[:800]  # Trim to avoid huge messages

    except Exception as e:
        return f"Error fetching PNR {pnr}: {str(e)}"