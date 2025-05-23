from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext
)
from config.settings import Config
from config.constants import Messages, Buttons
from database.operations import DBOperations
from ..keyboards import create_reply_markup, get_back_button

# Customer conversation states
SEARCH_CUSTOMER, VIEW_CUSTOMER = range(2)

class CustomerHandler:
    @staticmethod
    def create_customer_conversation():
        return ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^👤 Customers$"), CustomerHandler.start_customer_search)],
            states={
                SEARCH_CUSTOMER: [MessageHandler(filters.TEXT & ~filters.COMMAND, CustomerHandler.search_customer)],
                VIEW_CUSTOMER: [
                    MessageHandler(filters.Regex("^📝 Edit$"), CustomerHandler.edit_customer),
                    MessageHandler(filters.Regex("^📊 History$"), CustomerHandler.view_history)
                ]
            },
            fallbacks=[CommandHandler("cancel", CustomerHandler.cancel_customer_search)],
            allow_reentry=True
        )

    @staticmethod
    async def start_customer_search(update: Update, context: CallbackContext):
        """Start customer search process"""
        await update.message.reply_text(
            "Enter customer phone number or name:",
            reply_markup=get_back_button()
        )
        return SEARCH_CUSTOMER

    @staticmethod
    async def search_customer(update: Update, context: CallbackContext):
        """Search for customer by phone or name"""
        search_term = update.message.text
        
        # Try phone first
        if search_term.isdigit() and len(search_term) == 10:
            customer = DBOperations.get_customer_by_phone(search_term)
        else:
            customer = DBOperations.search_customer_by_name(search_term)
        
        if not customer:
            await update.message.reply_text(
                "Customer not found. Try again:",
                reply_markup=get_back_button()
            )
            return SEARCH_CUSTOMER
        
        context.user_data['current_customer'] = customer
        
        message = (
            f"<b>Customer Found:</b>\n\n"
            f"Name: {customer['name']}\n"
            f"Phone: {customer['phone'] or 'Not provided'}\n"
            f"Total Spent: {customer['total_spent']}\n"
            f"Last Purchase: {customer['last_purchase'] or 'Never'}\n\n"
            f"Select an action:"
        )
        
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=create_reply_markup([["📝 Edit", "📊 History"], [Buttons.BACK]])
        )
        return VIEW_CUSTOMER

    @staticmethod
    async def edit_customer(update: Update, context: CallbackContext):
        """Edit customer details"""
        customer = context.user_data['current_customer']
        await update.message.reply_text(
            f"Editing {customer['name']}\n"
            f"Send new name or phone in format:\n"
            f"<code>Name, Phone</code>\n\n"
            f"Current: {customer['name']}, {customer['phone']}",
            parse_mode='HTML',
            reply_markup=get_back_button()
        )
        return VIEW_CUSTOMER

    @staticmethod
    async def view_history(update: Update, context: CallbackContext):
        """View customer purchase history"""
        customer = context.user_data['current_customer']
        history = DBOperations.get_customer_history(customer['id'])
        
        if not history:
            message = "No purchase history found."
        else:
            message = f"<b>Purchase History for {customer['name']}:</b>\n\n"
            for purchase in history:
                message += (
                    f"{purchase['date']} - "
                    f"Bill #{purchase['bill_number']}\n"
                    f"Items: {purchase['item_count']} - "
                    f"Total: {purchase['amount']}\n\n"
                )
        
        await update.message.reply_text(
            message,
            parse_mode='HTML',
            reply_markup=create_reply_markup([["📝 Edit", "📊 History"], [Buttons.BACK]])
        )
        return VIEW_CUSTOMER

    @staticmethod
    async def cancel_customer_search(update: Update, context: CallbackContext):
        """Cancel customer search"""
        context.user_data.pop('current_customer', None)
        
        await update.message.reply_text(
            "Customer search cancelled.",
            reply_markup=create_reply_markup(Buttons.MAIN_MENU)
        )
        return ConversationHandler.END