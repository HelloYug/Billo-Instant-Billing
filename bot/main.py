import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)

from config.settings import Config
from config.constants import Messages, Buttons
from database.operations import DBOperations
from .keyboards import create_reply_markup
from .handlers import (
    billing,
    inventory,
    customer
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class RetailBot:
    def __init__(self):
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        
        # Conversation handlers
        self.application.add_handler(billing.create_billing_conversation())
        self.application.add_handler(inventory.create_inventory_conversation())
        
        # Message handlers
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, self.handle_message
        ))
    
    async def start(self, update: Update, context):
        """Send welcome message and main menu"""
        user = update.effective_user
        await update.message.reply_text(
            f"Hi {user.first_name}! {Messages.WELCOME}",
            reply_markup=create_reply_markup(Buttons.MAIN_MENU)
        )
    
    async def help(self, update: Update, context):
        """Send help message"""
        help_text = (
            "🤖 <b>Retail Bot Help</b>\n\n"
            "• Use /start to see main menu\n"
            "• <b>Generate Bill</b> - Create a new customer bill\n"
            "• <b>Inventory</b> - Manage product stock\n"
            "• <b>Reports</b> - View sales reports\n"
        )
        await update.message.reply_text(help_text, parse_mode='HTML')
    
    async def handle_message(self, update: Update, context):
        """Handle all text messages"""
        text = update.message.text
        
        if text == "💰 Generate Bill":
            await billing.start_billing(update, context)
        elif text == "📦 Inventory":
            await inventory.start_inventory(update, context)
        elif text == Buttons.BACK:
            await self.start(update, context)
        else:
            await update.message.reply_text(Messages.INVALID_INPUT)

def main():
    """Run the bot"""
    bot = RetailBot()
    
    # Start the Bot
    bot.application.run_polling()

if __name__ == '__main__':
    main()