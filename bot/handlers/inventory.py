from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler
)
from config.settings import Config
from config.constants import Messages, Buttons
from database.operations import DBOperations
from ..keyboards import create_reply_markup, get_back_button

# Inventory conversation states
SELECT_ACTION, SELECT_PRODUCT, UPDATE_STOCK = range(3)

class InventoryHandler:
    @staticmethod
    def create_inventory_conversation():
        return ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^📦 Inventory$"), InventoryHandler.start_inventory)],
            states={
                SELECT_ACTION: [
                    MessageHandler(filters.Regex("^📥 Add Stock$"), InventoryHandler.add_stock),
                    MessageHandler(filters.Regex("^📤 Remove Stock$"), InventoryHandler.remove_stock),
                    MessageHandler(filters.Regex("^🔍 View Stock$"), InventoryHandler.view_stock)
                ],
                SELECT_PRODUCT: [
                    CallbackQueryHandler(InventoryHandler.handle_product_selection, pattern="^product_"),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, InventoryHandler.search_product)
                ],
                UPDATE_STOCK: [MessageHandler(filters.TEXT & ~filters.COMMAND, InventoryHandler.process_stock_update)]
            },
            fallbacks=[CommandHandler("cancel", InventoryHandler.cancel_inventory)],
            allow_reentry=True
        )

    @staticmethod
    async def start_inventory(update: Update, context: CallbackContext):
        """Start inventory management"""
        actions = [
            ["📥 Add Stock", "📤 Remove Stock"],
            ["🔍 View Stock", Buttons.BACK]
        ]
        await update.message.reply_text(
            "🛒 Inventory Management",
            reply_markup=create_reply_markup(actions)
        )
        return SELECT_ACTION

    @staticmethod
    async def add_stock(update: Update, context: CallbackContext):
        """Start adding stock process"""
        context.user_data['inventory_action'] = 'add'
        await update.message.reply_text(
            "Search for product by name or scan barcode:",
            reply_markup=get_back_button()
        )
        return SELECT_PRODUCT

    @staticmethod
    async def remove_stock(update: Update, context: CallbackContext):
        """Start removing stock process"""
        context.user_data['inventory_action'] = 'remove'
        await update.message.reply_text(
            "Search for product by name or scan barcode:",
            reply_markup=get_back_button()
        )
        return SELECT_PRODUCT

    @staticmethod
    async def view_stock(update: Update, context: CallbackContext):
        """View product stock"""
        products = DBOperations.get_low_stock_products()
        
        if not products:
            await update.message.reply_text(
                "No low stock items found.",
                reply_markup=create_reply_markup(Buttons.MAIN_MENU)
            )
            return ConversationHandler.END
        
        message = "<b>Low Stock Items:</b>\n\n"
        for product in products:
            message += (
                f"{product['name']} - "
                f"Stock: {product['stock']} "
                f"(Min: {product['min_stock']})\n"
            )
        
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=create_reply_markup(Buttons.MAIN_MENU)
        )
        return ConversationHandler.END

    @staticmethod
    async def search_product(update: Update, context: CallbackContext):
        """Search for product by name"""
        search_term = update.message.text
        products = DBOperations.search_products(search_term)
        
        if not products:
            await update.message.reply_text(
                "No products found. Try again:",
                reply_markup=get_back_button()
            )
            return SELECT_PRODUCT
        
        keyboard = [
            [InlineKeyboardButton(
                f"{p['name']} (Stock: {p['stock']})", 
                callback_data=f"product_{p['id']}"
            )]
            for p in products
        ]
        keyboard.append([InlineKeyboardButton(Buttons.BACK, callback_data="back_to_actions")])
        
        await update.message.reply_text(
            "Select product:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return SELECT_PRODUCT

    @staticmethod
    async def handle_product_selection(update: Update, context: CallbackContext):
        """Handle product selection from inline keyboard"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("product_"):
            product_id = int(query.data.split("_")[1])
            product = DBOperations.get_product_details(product_id)
            context.user_data['current_product'] = product
            
            action = context.user_data['inventory_action']
            action_text = "add to" if action == 'add' else "remove from"
            
            await query.edit_message_text(
                f"Product: {product['name']}\n"
                f"Current stock: {product['stock']}\n\n"
                f"Enter quantity to {action_text} stock:",
                reply_markup=None
            )
            return UPDATE_STOCK
        
        elif query.data == "back_to_actions":
            await InventoryHandler.start_inventory(update, context)
            return SELECT_ACTION

    @staticmethod
    async def process_stock_update(update: Update, context: CallbackContext):
        """Process stock update (add/remove)"""
        try:
            quantity = int(update.message.text)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            product = context.user_data['current_product']
            action = context.user_data['inventory_action']
            
            if action == 'remove' and quantity > product['stock']:
                await update.message.reply_text(
                    f"Cannot remove more than current stock ({product['stock']})!",
                    reply_markup=get_back_button()
                )
                return UPDATE_STOCK
            
            # Update stock in database
            adjustment = quantity if action == 'add' else -quantity
            DBOperations.update_stock(product['id'], adjustment)
            
            # Get updated product info
            updated_product = DBOperations.get_product_details(product['id'])
            
            await update.message.reply_text(
                f"Stock updated successfully!\n"
                f"{product['name']} - New stock: {updated_product['stock']}",
                reply_markup=create_reply_markup(Buttons.MAIN_MENU)
            )
            
            return ConversationHandler.END
            
        except ValueError:
            await update.message.reply_text(
                "Invalid quantity! Please enter a positive number.",
                reply_markup=get_back_button()
            )
            return UPDATE_STOCK

    @staticmethod
    async def cancel_inventory(update: Update, context: CallbackContext):
        """Cancel inventory management"""
        context.user_data.pop('inventory_action', None)
        context.user_data.pop('current_product', None)
        
        await update.message.reply_text(
            "Inventory management cancelled.",
            reply_markup=create_reply_markup(Buttons.MAIN_MENU)
        )
        return ConversationHandler.END