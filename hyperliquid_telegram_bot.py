import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import json

# Hyperliquid API endpoint
HYPERLIQUID_API = "https://api.hyperliquid.xyz/info"

# Target coins
TARGET_COINS = ['BTC', 'ETH', 'SOL', 'HYPE', 'FARTCOIN']

def get_vault_positions():
    """Fetch vault positions from Hyperliquid"""
    try:
        # Get all vaults
        vaults_payload = {
            "type": "vaultDetails"
        }
        
        response = requests.post(HYPERLIQUID_API, json=vaults_payload)
        vaults_data = response.json()
        
        leader_vaults = []
        
        # Filter for leader vaults and get their positions
        for vault in vaults_data:
            vault_address = vault.get('vault')
            vault_name = vault.get('name', 'Unknown')
            
            # Get vault positions
            positions_payload = {
                "type": "clearinghouseState",
                "user": vault_address
            }
            
            pos_response = requests.post(HYPERLIQUID_API, json=positions_payload)
            positions_data = pos_response.json()
            
            # Filter positions for target coins
            if 'assetPositions' in positions_data:
                filtered_positions = []
                for pos in positions_data['assetPositions']:
                    coin = pos['position']['coin']
                    # Check if coin matches any target (handling both spot and perp formats)
                    for target in TARGET_COINS:
                        if target in coin.upper():
                            filtered_positions.append(pos)
                            break
                
                if filtered_positions:
                    leader_vaults.append({
                        'name': vault_name,
                        'address': vault_address,
                        'positions': filtered_positions
                    })
        
        return leader_vaults
    
    except Exception as e:
        print(f"Error fetching vault positions: {e}")
        return []

def format_position_message(vaults):
    """Format vault positions into a readable message"""
    if not vaults:
        return "No leader vault positions found for the specified coins."
    
    message = "🏆 *Hyperliquid Leader Vault Positions*\n\n"
    
    for vault in vaults:
        message += f"📊 *{vault['name']}*\n"
        message += f"_Vault: {vault['address'][:8]}...{vault['address'][-6:]}_\n\n"
        
        for pos in vault['positions']:
            position = pos['position']
            coin = position['coin']
            size = float(position['szi'])
            entry_px = float(position.get('entryPx', 0))
            
            position_type = "🟢 LONG" if size > 0 else "🔴 SHORT"
            
            message += f"  {position_type} {coin}\n"
            message += f"  Size: {abs(size):.4f}\n"
            message += f"  Entry: ${entry_px:.2f}\n"
            
            if 'unrealizedPnl' in position:
                pnl = float(position['unrealizedPnl'])
                pnl_emoji = "💚" if pnl > 0 else "❌"
                message += f"  PnL: {pnl_emoji} ${pnl:.2f}\n"
            
            message += "\n"
        
        message += "─" * 30 + "\n\n"
    
    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Welcome to Hyperliquid Leader Vaults Bot!\n\n"
        "Commands:\n"
        "/positions - Get current positions for BTC, ETH, SOL, HYPE, FARTCOIN\n"
        "/help - Show this help message"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "📖 *Help*\n\n"
        "/positions - Fetch and display leader vault positions\n"
        "/start - Show welcome message\n"
        "/help - Show this help message\n\n"
        "Tracking: BTC, ETH, SOL, HYPE, FARTCOIN",
        parse_mode='Markdown'
    )

async def positions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and send vault positions."""
    await update.message.reply_text("🔍 Fetching positions from Hyperliquid...")
    
    vaults = get_vault_positions()
    message = format_position_message(vaults)
    
    # Split message if too long (Telegram limit is 4096 chars)
    if len(message) > 4096:
        parts = [message[i:i+4096] for i in range(0, len(message), 4096)]
        for part in parts:
            await update.message.reply_text(part, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, parse_mode='Markdown')

def main():
    """Start the bot."""
    # Get token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set")
        print("\nTo set it:")
        print("export TELEGRAM_BOT_TOKEN='your-bot-token-here'")
        return
    
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
