# Tour Bot Deployment Guide

## ⚠️ IMPORTANT - Before Deploying

**Fix the TOKEN in `tour_bot.py`:**
- Line 14 has a space in the token: `"8911797784:AAH12z6PnSdqCX6pi_50s66EAt YhLMRcEN4"`
- Remove the space between "EAt" and "YhLMRcEN4"
- Correct token: `"8911797784:AAH12z6PnSdqCX6pi_50s66EAtYhLMRcEN4"`

---

## Option 1: Deploy to Render.com (Recommended - Free)

### Step 1: Prepare Files
```
Your project folder should contain:
├── tour_bot.py
├── requirements.txt
└── .gitignore (optional)
```

### Step 2: Create Git Repository (Local)
```bash
git init
git add .
git commit -m "Initial commit: Tour bot setup"
```

### Step 3: Push to GitHub
1. Create a new repository on GitHub (https://github.com/new)
2. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/tour-bot.git
git branch -M main
git push -u origin main
```

### Step 4: Deploy to Render
1. Go to https://render.com (sign up with GitHub)
2. Click **New +** → **Web Service**
3. Connect GitHub repository
4. Configure:
   - **Name:** tour-bot
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python tour_bot.py`
5. Click **Create Web Service**
6. Wait for deployment (1-2 minutes)

---

## Option 2: Deploy to Replit

1. Go to https://replit.com
2. Click **Create** → **Import from GitHub**
3. Paste your repository URL
4. Click **Import**
5. Replit will auto-detect Python
6. Click **Run** (top button)
7. Bot runs in the console

---

## Testing Your Bot

### Test 1: Send a Message to Your Channel
1. Open your Telegram channel (@rrturlarbot is in admin list)
2. Post a test message:
   ```
   Paris Turu
   Qiyməti: 5000 AZN
   3 günlük paket
   ```
3. Bot should respond in console with: `Tour processed: 5000 → 5150 AZN`
4. Check your channel - formatted message should appear

### Test 2: Check Bot Logs
- **Render:** Dashboard → Logs tab
- **Replit:** Bottom console panel shows real-time output

---

## Common Issues

### Bot Not Responding?
- Check TOKEN is correct (no spaces)
- Verify bot is added to channel as **Admin**
- Check Render/Replit logs for errors

### Message Not Formatting?
- Ensure message contains number + "AZN" or "₼"
- Example: "2500 AZN" ✅ works
- Example: "Price: 2500" ❌ won't work

### Webhook vs Polling?
- Current code uses `polling` (simpler for free tier)
- No need to change - polling works fine for free hosting

---

## Next Steps After Testing

1. ✅ Bot automatically processes incoming messages
2. **Manual Step:** Copy formatted message to WhatsApp channel
3. **OR** Set up WhatsApp API later for full automation

---

## Monitoring Your Bot

**To keep bot running 24/7:**
- **Render:** Free tier spins down after 15 min of inactivity
  - Solution: Upgrade to Hobby ($7/month) for always-on
- **Replit:** Free tier also has limits
  - Solution: Use Replit Pro or Render

---

## Environment Variables (Optional Enhancement)

Create `.env` file:
```
TELEGRAM_TOKEN=8911797784:AAH12z6PnSdqCX6pi_50s66EAtYhLMRcEN4
TELEGRAM_CHANNEL=-1003303207925
MARKUP_AZN=150
```

Then update `tour_bot.py`:
```python
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL = int(os.getenv("TELEGRAM_CHANNEL"))
MARKUP_AZN = int(os.getenv("MARKUP_AZN"))
```

This keeps secrets out of code! 🔒

---

**Ready?** Choose Render or Replit and start deployment!
