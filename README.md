# 🚆 PNR Tracker Bot → Zoho Cliq (100% Free)

A simple, serverless bot that tracks Indian Railway PNR status and sends updates to Zoho Cliq.

Built using:

* GitHub Actions (scheduler)
* Python + Playwright (scraping)
* Zoho Cliq Bot (notifications)

---

## 🧠 Features

* ✅ Track multiple PNR numbers
* ✅ Sends updates only when status changes
* ✅ Fully free (no paid APIs)
* ✅ Runs automatically every hour
* ✅ Generic notification system (reusable for other use cases)

---

## 🏗️ Architecture

```
GitHub Actions (cron)
        ↓
Python Script
        ↓
PNR Scraper (Playwright)
        ↓
Change Detection (state.json)
        ↓
Zoho Cliq Webhook
```

---

## 📁 Project Structure

```
pnr-cliq-bot/
├── main.py                # Core logic
├── scraper.py            # Fetch PNR status
├── notifier.py           # Send notifications
├── state.json            # Stores last known state
├── requirements.txt      # Dependencies
└── .github/workflows/
    └── cron.yml          # Scheduler
```

---

## ⚙️ Setup Guide

### 1. Clone Repository

```
git clone https://github.com/<your-username>/pnr-cliq-bot.git
cd pnr-cliq-bot
```

---

### 2. Create Zoho Cliq Bot

In Zoho Cliq:

1. Create a bot
2. Enable **Incoming Webhook**
3. Copy webhook URL

Example:

```
https://cliq.zoho.in/api/v2/bots/pnrbot/incoming?zapikey=XXXX
```

---

### 3. Configure GitHub Secrets

Go to:

```
Repo → Settings → Secrets → Actions
```

Add:

#### 🔑 `PNR_LIST`

```
1234567890,9876543210
```

#### 🔑 `ZOHO_WEBHOOK_URL`

```
https://cliq.zoho.in/api/v2/bots/pnrbot/incoming?zapikey=XXXX
```

---

### 4. Run GitHub Action

* Go to **Actions tab**
* Click **Run Workflow**

OR wait for scheduled execution (every hour)

---

## 🧪 Example Notification

```
ℹ️ 🚆 PNR 1234567890 Update

Passenger 1: CNF
Passenger 2: RAC

_Source: pnr-tracker_
```

---

## 🔄 How It Works

* Script fetches PNR status using scraping
* Compares with previous state (`state.json`)
* Sends update only if status changes
* Saves new state back to repository

---

## ⚠️ Important Notes

* This project uses **web scraping**, not official APIs
* Website structure changes may break parsing
* GitHub Actions is stateless → state is persisted via commits
* Avoid running too frequently (hourly is safe)

---

## 🚀 Future Improvements

* Parse structured passenger status (instead of raw text)
* Notify only on meaningful changes (WL → CNF)
* Add CLIQ commands (`/track pnr`)
* Multi-user support
* Dashboard UI

---

## 🏆 Why This Project?

This is a minimal, real-world example of:

* Event-driven automation
* Serverless architecture
* Generic notification pipelines

---

## 📜 License

MIT License

---

## 🤝 Contributing

Feel free to fork, improve, and extend this project.

---

## 💡 Inspiration

Built as a simple, free alternative to paid railway APIs and automation tools.
