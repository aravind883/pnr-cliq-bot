def send_notification(data):
    print("Sending payload:", data)

    response = requests.post(ZOHO_WEBHOOK, json=data)

    print("Status Code:", response.status_code)
    print("Response:", response.text)