import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import json

# Hyperliquid API endpoint
HYPERLIQUID_API = "https://api.hyperliquid.xyz/info"

# Specific vault address to track
VAULT_ADDRESS = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"

# Target coins
TARGET_COINS = ['BTC', 'ETH', 'SOL', 'HYPE', 'FARTCOIN']

def get_vault_positions():
    try:
        payload = {
            "type": "vaultState",
            "vaultAddress": VAULT_ADDRESS
        }

        response = requests.post(
            HYPERLIQUID_API,
            json=payload,
            timeout=10
        )

        data = response.json()

        asset_positions = data.get("assetPositions", [])

        if not asset_positions:
            print("❌ vaultState returned no positions")
            return []

        filtered_positions = []
        for pos in asset_positions:
            position = pos.get("position", {})
            coin = position.get("coin", "").upper()

            if coin in TARGET_COINS:
                filtered_positions.append(pos)
                print(f"✓ Found {coin}")

        if not filtered_positions:
            print("❌ No target coin positions found")
            return []

        return [{
            "name": data.get("name", "Vault"),
            "address": VAULT_ADDRESS,
            "positions": filtered_positions
        }]

    except Exception as e:
        print("❌ Error fetching vaultState:", e)
        return []

def format_position_message(vaults):
    """Format vault positions into a readable message"""
    if not vaults:
        return f"❌ No positions found for tracked coins in vault.\n\nVault: `{VAULT_ADDRESS}`\nTracking: BTC, ETH, SOL, HYPE, FARTCOIN"
    
    vault = vaults[0]
    message = "🏆 *Hyperliquid Vault Positions*\n\n"
    message += f"📊 *{vault['name']}*\n"
    message += f"_Vault: `{vault['address'][:8]}...{vault['address'][-6:]}`_\n\n"
    
    for pos in vault['positions']:
        position = pos.get('position', {})
        coin = position.get('coin', 'Unknown')
        size = float(position.get('szi', 0))
        entry_px = float(position.get('entryPx', 0))
        
        position_type = "🟢 LONG" if size > 0 else "🔴 SHORT"
        
        message += f"{position_type} *{coin}*\n"
        message += f"Size: `{abs(size):.4f}`\n"
        
        if entry_px > 0:
            message += f"Entry: `${entry_px:.2f}`\n"
        
        unrealized_pnl = position.get('unrealizedPnl')
        if unrealized_pnl:
            pnl = float(unrealized_pnl)
            pnl_emoji = "💚" if pnl > 0 else "❌"
            message += f"PnL: {pnl_emoji} `${pnl:.2f}`\n"
        
        message += "\n"
    
    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Welcome to Hyperliquid Vault Tracker Bot!\n\n"
        "Commands:\n"
        "/positions - Get current vault positions\n"
        "/help - Show this help message\n\n"
        f"Tracking vault: {VAULT_ADDRESS[:8]}...{VAULT_ADDRESS[-6:]}\n"
        "Coins: BTC, ETH, SOL, HYPE, FARTCOIN"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "📖 *Help*\n\n"
        "/positions - Fetch and display vault positions\n"
        "/start - Show welcome message\n"
        "/help - Show this help message\n\n"
        f"Vault: `{VAULT_ADDRESS}`\n"
        "Tracking: BTC, ETH, SOL, HYPE, FARTCOIN",
        parse_mode='Markdown'
    )

async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and send vault positions."""
    loading_msg = await update.message.reply_text("🔍 Fetching positions from Hyperliquid...")
    
    try:
        vaults = get_vault_positions()
        message = format_position_message(vaults)
        
        # Delete loading message
        await loading_msg.delete()
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    except Exception as e:
        await loading_msg.delete()
        await update.message.reply_text(f"❌ Error fetching positions: {str(e)}")
        print(f"Error in positions command: {e}")

def main():
    """Start the bot."""
    # Get token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set")
        print("\nTo set it:")
        print("export TELEGRAM_BOT_TOKEN='your-bot-token-here'")
        return
    
    print(f"Starting bot...")
    print(f"Tracking vault: {VAULT_ADDRESS}")
    print(f"Target coins: {', '.join(TARGET_COINS)}")
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("positions", positions))
    
    print("Bot is running... Press Ctrl+C to stop")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
