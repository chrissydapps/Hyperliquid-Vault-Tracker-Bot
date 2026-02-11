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
    """Fetch positions for the specific vault"""
    try:
        # Get vault details
        vault_details_payload = {
            "type": "vaultDetails",
            "vaultAddress": VAULT_ADDRESS
        }
        
        print(f"Fetching details for vault: {VAULT_ADDRESS}")
        
        # Try to get vault name
        try:
            details_response = requests.post(HYPERLIQUID_API, json=vault_details_payload, timeout=10)
            vault_info = details_response.json()
            vault_name = vault_info.get('name', 'Unknown Vault') if isinstance(vault_info, dict) else 'Unknown Vault'
        except:
            vault_name = 'Unknown Vault'
        
        print(f"Vault name: {vault_name}")
        
        # Get vault positions
        positions_payload = {
            "type": "clearinghouseState",
            "user": VAULT_ADDRESS
        }
        
        pos_response = requests.post(HYPERLIQUID_API, json=positions_payload, timeout=10)
        positions_data = pos_response.json()
        
        print(f"Got response: {positions_data.keys() if isinstance(positions_data, dict) else 'Not a dict'}")
        
        # Filter positions for target coins
        filtered_positions = []
        
        if 'assetPositions' in positions_data and positions_data['assetPositions']:
            print(f"Found {len(positions_data['assetPositions'])} total positions")
            
            for pos in positions_data['assetPositions']:
                position = pos.get('position', {})
                coin = position.get('coin', '').upper()
                
                print(f"  Checking coin: {coin}")
                
                # Check if coin matches any target
                for target in TARGET_COINS:
                    if target in coin:
                        filtered_positions.append(pos)
                        print(f"  ✓ Matched {target}")
                        break
        else:
            print("No assetPositions found in response")
        
        print(f"Filtered to {len(filtered_positions)} target positions")
        
        if filtered_positions:
            return [{
                'name': vault_name,
                'address': VAULT_ADDRESS,
                'positions': filtered_positions
            }]
        
        return []
    
    except Exception as e:
        print(f"Error fetching vault positions: {e}")
        import traceback
        traceback.print_exc()
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
