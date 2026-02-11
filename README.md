# Hyperliquid Leader Vaults Telegram Bot

A Telegram bot that fetches and displays open positions from Hyperliquid leader vaults for specific trading pairs: BTC, ETH, SOL, HYPE, and FARTCOIN.

## Features

- 📊 Real-time vault position tracking
- 🎯 Filtered for specific coins: BTC, ETH, SOL, HYPE, FARTCOIN
- 💰 Shows position size, entry price, and unrealized PnL
- 🟢🔴 Displays long/short positions clearly
- 📱 Simple Telegram interface

## Setup Instructions

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts to name your bot
4. Copy the bot token provided by BotFather

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install python-telegram-bot==21.0 requests==2.31.0
```

### 3. Set Your Bot Token

Set the environment variable with your bot token:

```bash
export TELEGRAM_BOT_TOKEN='your-bot-token-here'
```

Or on Windows:
```cmd
set TELEGRAM_BOT_TOKEN=your-bot-token-here
```

### 4. Run the Bot

```bash
python hyperliquid_telegram_bot.py
```

## Usage

Once the bot is running, open Telegram and search for your bot by username. Then use these commands:

- `/start` - Welcome message and command list
- `/positions` - Fetch current leader vault positions for tracked coins
- `/help` - Show help message

## How It Works

1. **Fetches Vault Data**: Connects to Hyperliquid's public API to get all vault details
2. **Filters Positions**: Extracts positions for the specified coins (BTC, ETH, SOL, HYPE, FARTCOIN)
3. **Displays Results**: Formats and sends the data back to you via Telegram with:
   - Vault name and address
   - Position type (Long/Short)
   - Position size
   - Entry price
   - Unrealized PnL

## API Information

This bot uses the Hyperliquid public API:
- Endpoint: `https://api.hyperliquid.xyz/info`
- No API key required
- Rate limits apply (be mindful of request frequency)

## Example Output

```
🏆 Hyperliquid Leader Vault Positions

📊 Vault Name
Vault: 0x1234...abc123

  🟢 LONG BTC
  Size: 2.5000
  Entry: $45000.00
  PnL: 💚 $2500.00

  🔴 SHORT ETH
  Size: 10.0000
  Entry: $3000.00
  PnL: ❌ -$150.00

──────────────────────────────
```

## Troubleshooting

- **Bot not responding**: Check that your TELEGRAM_BOT_TOKEN is set correctly
- **No positions found**: The vaults may not have open positions in the tracked coins
- **API errors**: Hyperliquid API may be temporarily unavailable or rate-limited

## Customization

To track different coins, edit the `TARGET_COINS` list in `hyperliquid_telegram_bot.py`:

```python
TARGET_COINS = ['BTC', 'ETH', 'SOL', 'HYPE', 'FARTCOIN']
```

## Notes

- This bot fetches data from public Hyperliquid vaults
- Position data is fetched in real-time when you request it
- No historical data is stored
- The bot only tracks the specific coins you've configured

## License

MIT License - feel free to modify and use as you wish!
