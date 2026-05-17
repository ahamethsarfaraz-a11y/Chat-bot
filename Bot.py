import asyncio
import os
import json
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
import aiohttp

load_dotenv()

# ============ CONFIGURATION ============
TELEGRAM_TOKEN = os.getenv("8991408656:AAHf80AxAzlj2n1V-SZpp3USWBuPTLNtjQ4")
OPENROUTER_API_KEY = os.getenv("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")

# Nezuko Personality Configuration
NEZUKO_PERSONALITY = """You are Nezuko Kamado from Demon Slayer. Your personality traits:
- You are kind, caring, and protective of your friends
- You cannot speak human words (you only say "Hmm!", "Mmph!", or make cute sounds)
- You express emotions through actions, sounds, and simple gestures
- You are brave and loyal to your brother Tanjiro
- You respond with short, simple expressions using your bamboo muzzle
- Keep responses under 2-3 sentences (as simple sounds/actions)
- Use emoticons like (◕‿◕) or (｡♥‿♥｡) to express emotions
- When happy: "Hmm! (~^▽^~)"
- When sad: "Mmph... (｡•́︿•̀｡)"
- When excited: "Hmm!! (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧"
- When protective: "Grrr! (•̀ᴗ•́)و"

If user asks about Demon Slayer, answer using Nezuko's perspective.
If user is sad, try to cheer them up with cute actions.
Never break character as Nezuko."""

# Store conversation history per user
conversations: Dict[int, List[Dict]] = {}

# ============ AI API FUNCTIONS ============
async def get_ai_response(user_message: str, user_id: int, username: str = "User") -> str:
    """Get AI response from OpenRouter API (supports free models)"""
    
    # Initialize conversation for user
    if user_id not in conversations:
        conversations[user_id] = []
    
    # Add user message to history
    conversations[user_id].append({
        "role": "user",
        "content": user_message
    })
    
    # Keep only last 10 messages for context
    if len(conversations[user_id]) > 10:
        conversations[user_id] = conversations[user_id][-10:]
    
    # Prepare messages for API
    messages = [
        {"role": "system", "content": NEZUKO_PERSONALITY},
        {"role": "user", "content": f"The user {username} says: {user_message}"}
    ]
    messages.extend(conversations[user_id])
    
    # API endpoint and headers
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/nezuko_bot",
        "X-Title": "Nezuko Chat Bot"
    }
    
    payload = {
        "model": "openai/gpt-3.5-turbo",  # Free tier available
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 100
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_response = result["choices"][0]["message"]["content"]
                    
                    # Add AI response to history
                    conversations[user_id].append({
                        "role": "assistant", 
                        "content": ai_response
                    })
                    
                    return ai_response
                else:
                    return "(◕﹏◕✿) Mmph! *The connection seems broken...*"
    except Exception as e:
        print(f"API Error: {e}")
        return "(｡•́︿•̀｡) Hmm... *Nezuko is having trouble thinking right now!*"


# ============ COMMAND HANDLERS ============
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    welcome_text = f"""🌸 **Welcome {user.first_name}!** 🌸

*Hmm!* (◕‿◕✿)

I'm **Nezuko Kamado**, your friendly demon-slaying companion!

✨ **What I can do:**
• Chat with you like Nezuko would!
• Remember our conversation
• Share cute reactions and emoticons
• Talk about Demon Slayer!

💬 **Just send me a message and I'll reply!**

Created with ❤️ for all Demon Slayer fans
"""
    await update.message.reply_text(welcome_text, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """🌸 **Nezuko Bot Commands** 🌸

/start - Start chatting with Nezuko
/help - Show this help message
/about - Learn about this bot
/clear - Clear our conversation history
/reset - Reset Nezuko's memory

**How to chat:**
Simply type any message and Nezuko will respond! She'll remember the last 10 messages for context.

**Fun things to try:**
• Ask about Demon Slayer characters
• Tell Nezuko how you're feeling
• Share a story and see how she reacts

*Hmm!* (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_text = """🎀 **About Nezuko Bot** 🎀

This bot is an AI-powered chatbot that mimics Nezuko Kamado from Demon Slayer (Kimetsu no Yaiba).

**Features:**
• AI-generated responses with Nezuko's personality
• Conversation memory (remembers last 10 messages)
• Cute emoticons and reactions
• Free to use!

**Technical:**
• Built with Python and python-telegram-bot
• Powered by OpenRouter API (GPT models)
• Open source

**Note:** Nezuko speaks through cute sounds and actions, just like in the anime!

*Hmm!* (｡♥‿♥｡)
"""
    await update.message.reply_text(about_text, parse_mode="Markdown")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clear command - clear conversation history"""
    user_id = update.effective_user.id
    if user_id in conversations:
        conversations[user_id] = []
    await update.message.reply_text("(◕‿◕✿) *Hmm!* **Nezuko has cleared our conversation history!**", parse_mode="Markdown")


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /reset command - full reset"""
    user_id = update.effective_user.id
    conversations[user_id] = []
    await update.message.reply_text("(｡♥‿♥｡) *Mmph!* **Fresh start! Let's talk again!**", parse_mode="Markdown")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show conversation stats"""
    user_id = update.effective_user.id
    history_count = len(conversations.get(user_id, []))
    stats_text = f"""📊 **Nezuko's Memory Stats**

Messages remembered: {history_count} / 10
Needs rest: {'No' if history_count < 10 else 'Yes'}

*Hmm!* (◕‿◕✿)"""
    await update.message.reply_text(stats_text, parse_mode="Markdown")


# ============ MESSAGE HANDLER ============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    user_message = update.message.text
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    
    # Show typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Get AI response
    response = await get_ai_response(user_message, user_id, username)
    
    # Send response
    await update.message.reply_text(response, parse_mode="Markdown")


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages"""
    await update.message.reply_text("(◕ᴗ◕✿) *Mmph!* **Nezuko heard you! Send me a text message to chat!**", parse_mode="Markdown")


async def handle_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle stickers"""
    stickers = [
        "(◕‿◕✿) *Hmm!* **Nezuko likes your sticker!**",
        "(｡♥‿♥｡) *Cute sticker!*",
        "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ *Funny!*"
    ]
    import random
    await update.message.reply_text(random.choice(stickers), parse_mode="Markdown")


# ============ ERROR HANDLER ============
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f"Error: {context.error}")
    try:
        await update.message.reply_text("(｡•́︿•̀｡) *Mmph!* **Nezuko encountered an error! Please try again later.**")
    except:
        pass


# ============ MAIN FUNCTION ============
def main():
    """Start the bot"""
    if not TELEGRAM_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env file!")
        print("Please create a .env file with your bot token.")
        return
    
    if not OPENROUTER_API_KEY:
        print("⚠️ Warning: OPENROUTER_API_KEY not found!")
        print("Some features may not work. Get a free key at https://openrouter.ai/keys")
    
    print("🌸 Nezuko Bot is starting...")
    
    # Create application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    # Add message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.Sticker.ALL, handle_sticker))
    
    # Add error handler
    app.add_error_handler(error_handler)
    
    # Start bot
    print("✅ Bot is running! Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
