# Deploy to Render.com (Free)

## Step 1: Create Your Telegram Bot
1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Choose a name and username
4. **Copy the bot token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Step 2: Upload to GitHub
1. Go to [github.com](https://github.com) and sign in (create account if needed)
2. Click the `+` icon → "New repository"
3. Name it `hyperliquid-bot` (or anything you want)
4. Make it **Public**
5. Click "Create repository"
6. Click "uploading an existing file"
7. Upload these 3 files:
   - `hyperliquid_telegram_bot.py`
   - `requirements.txt`
   - `render.yaml`
8. Click "Commit changes"

## Step 3: Deploy on Render
1. Go to [render.com](https://render.com) and sign up (free, no credit card)
2. Click "New +" → "Web Service"
3. Click "Connect GitHub" and authorize
4. Find your `hyperliquid-bot` repo and click "Connect"
5. Render will auto-detect settings from `render.yaml`
6. Scroll down to "Environment Variables"
7. Add variable:
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: [paste your bot token from Step 1]
8. Click "Create Web Service"

## Step 4: Wait for Deployment
- Render will install dependencies and start your bot (takes 2-3 minutes)
- Look for "Your service is live" message
- Check logs to confirm bot is running

## Step 5: Test Your Bot
1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Send `/positions` to get vault data

## Troubleshooting
- **Bot not responding**: Check that TELEGRAM_BOT_TOKEN is set correctly in Render dashboard
- **Service crashes**: Check the logs in Render dashboard
- **Need to update code**: Push changes to GitHub, Render auto-deploys

## Notes
- Free tier sleeps after 15 min of inactivity, but wakes on first message
- To keep it always awake, upgrade to paid tier ($7/mo) or use a ping service
- Your bot will restart automatically if it crashes

## Cost
**$0/month** - Completely free!
