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
from utils.helpers import generate_bill_number, format_currency
from ..keyboards import create_reply_markup, get_back_button
from datetime import datetime

# Billing conversation states
ENTER_NAME, ENTER_PHONE, ADD_ITEMS, CONFIRM_BILL = range(4)

class BillingHandler:
    @staticmethod
    def create_billing_conversation():
        return ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^💰 Generate Bill$"), BillingHandler.start_billing)],
            states={
                ENTER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, BillingHandler.get_customer_name)],
                ENTER_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, BillingHandler.get_customer_phone)],
                ADD_ITEMS: [
                    MessageHandler(filters.Regex("^➕ Add Item$"), BillingHandler.add_item),
                    MessageHandler(filters.Regex("^✅ Finish Bill$"), BillingHandler.finish_bill),
                    CallbackQueryHandler(BillingHandler.handle_product_selection, pattern="^product_")
                ],
                CONFIRM_BILL: [MessageHandler(filters.TEXT & ~filters.COMMAND, BillingHandler.confirm_bill)]
            },
            fallbacks=[CommandHandler("cancel", BillingHandler.cancel_billing)],
            allow_reentry=True
        )

    @staticmethod
    async def start_billing(update: Update, context: CallbackContext):
        """Start the billing process"""
        context.user_data['bill'] = {
            'items': [],
            'total': 0,
            'discount': 0
        }
        await update.message.reply_text(
            Messages.ENTER_CUSTOMER_NAME,
            reply_markup=get_back_button()
        )
        return ENTER_NAME

    @staticmethod
    async def get_customer_name(update: Update, context: CallbackContext):
        """Store customer name and ask for phone"""
        context.user_data['bill']['customer_name'] = update.message.text
        await update.message.reply_text(
            Messages.ENTER_PHONE,
            reply_markup=create_reply_markup([[Buttons.BACK, "Skip"]])
        )
        return ENTER_PHONE

    @staticmethod
    async def get_customer_phone(update: Update, context: CallbackContext):
        """Store customer phone and show product categories"""
        phone = update.message.text.lower()
        if phone != "skip":
            context.user_data['bill']['customer_phone'] = phone
        
        categories = DBOperations.get_categories()
        keyboard = [
            [InlineKeyboardButton(cat['category'], callback_data=f"category_{cat['category']}")]
            for cat in categories
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Select a category:",
            reply_markup=reply_markup
        )
        return ADD_ITEMS

    @staticmethod
    async def handle_product_selection(update: Update, context: CallbackContext):
        """Handle product selection from inline keyboard"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("category_"):
            category = query.data.split("_")[1]
            products = DBOperations.get_products_by_category(category)
            
            keyboard = [
                [InlineKeyboardButton(
                    f"{prod['name']} ({format_currency(prod['price'])})", 
                    callback_data=f"product_{prod['id']}"
                )]
                for prod in products
            ]
            keyboard.append([InlineKeyboardButton(Buttons.BACK, callback_data="back_to_categories")])
            
            await query.edit_message_text(
                f"Products in {category}:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif query.data.startswith("product_"):
            product_id = int(query.data.split("_")[1])
            context.user_data['current_product'] = product_id
            await query.edit_message_text(
                "Enter quantity:",
                reply_markup=None
            )
        
        elif query.data == "back_to_categories":
            await BillingHandler.get_customer_phone(update, context)
        
        return ADD_ITEMS

    @staticmethod
    async def add_item(update: Update, context: CallbackContext):
        """Add item to the bill"""
        try:
            quantity = int(update.message.text)
            product_id = context.user_data['current_product']
            product = DBOperations.get_product_details(product_id)
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            if quantity > product['stock']:
                await update.message.reply_text(
                    f"Only {product['stock']} available in stock!",
                    reply_markup=get_back_button()
                )
                return ADD_ITEMS
            
            item = {
                'product_id': product_id,
                'name': product['name'],
                'quantity': quantity,
                'price': product['price'],
                'total': quantity * product['price']
            }
            
            context.user_data['bill']['items'].append(item)
            context.user_data['bill']['total'] += item['total']
            
            await update.message.reply_text(
                f"Added {quantity} x {product['name']} for {format_currency(item['total'])}\n"
                f"Current total: {format_currency(context.user_data['bill']['total'])}",
                reply_markup=create_reply_markup([["➕ Add Item", "✅ Finish Bill"], [Buttons.BACK]])
            )
            
            DBOperations.update_stock(product_id, quantity)
            
        except ValueError:
            await update.message.reply_text(
                "Invalid quantity! Please enter a positive number.",
                reply_markup=get_back_button()
            )
        
        return ADD_ITEMS

    @staticmethod
    async def finish_bill(update: Update, context: CallbackContext):
        """Finish the bill and show summary"""
        bill = context.user_data['bill']
        
        if not bill['items']:
            await update.message.reply_text(
                "No items added to bill!",
                reply_markup=get_back_button()
            )
            return ADD_ITEMS
        
        bill_text = f"<b>{Config.COMPANY_NAME} - Bill Summary</b>\n\n"
        bill_text += f"Customer: {bill.get('customer_name', 'Walk-in')}\n"
        
        if 'customer_phone' in bill:
            bill_text += f"Phone: {bill['customer_phone']}\n"
        
        bill_text += "\n<b>Items:</b>\n"
        for item in bill['items']:
            bill_text += (
                f"- {item['quantity']} x {item['name']} "
                f"@ {format_currency(item['price'])} = "
                f"{format_currency(item['total'])}\n"
            )
        
        bill_text += f"\n<b>Subtotal:</b> {format_currency(bill['total'])}\n"
        
        if bill['discount'] > 0:
            bill_text += f"<b>Discount:</b> -{format_currency(bill['discount'])}\n"
            bill_text += f"<b>Total:</b> {format_currency(bill['total'] - bill['discount'])}\n"
        else:
            bill_text += f"<b>Total:</b> {format_currency(bill['total'])}\n"
        
        bill_text += "\nEnter discount amount (or 0 for none):"
        
        await update.message.reply_text(
            bill_text,
            parse_mode='HTML',
            reply_markup=create_reply_markup([["0", "50", "100"], [Buttons.CANCEL]])
        )
        return CONFIRM_BILL

    @staticmethod
    async def confirm_bill(update: Update, context: CallbackContext):
        """Apply discount and save bill"""
        try:
            discount = float(update.message.text)
            if discount < 0:
                raise ValueError("Discount cannot be negative")
            
            bill = context.user_data['bill']
            bill['discount'] = min(discount, bill['total'])
            final_total = bill['total'] - bill['discount']
            
            # Save to database
            bill_number = generate_bill_number()
            bill_id = DBOperations.create_bill(
                customer_name=bill['customer_name'],
                customer_phone=bill.get('customer_phone'),
                items=bill['items']
            )
            
            # Generate receipt
            receipt = (
                f"<b>{Config.COMPANY_NAME}</b>\n"
                f"Bill No: {bill_number}\n"
                f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            )
            
            for item in bill['items']:
                receipt += (
                    f"{item['quantity']} x {item['name']} "
                    f"@ {format_currency(item['price'])} = "
                    f"{format_currency(item['total'])}\n"
                )
            
            receipt += (
                f"\nSubtotal: {format_currency(bill['total'])}\n"
                f"Discount: -{format_currency(bill['discount'])}\n"
                f"<b>Total: {format_currency(final_total)}</b>\n\n"
                f"Thank you for shopping with us!"
            )
            
            await update.message.reply_text(
                receipt,
                parse_mode='HTML',
                reply_markup=create_reply_markup(Buttons.MAIN_MENU)
            )
            
            # Clear bill data
            context.user_data.pop('bill', None)
            
            return ConversationHandler.END
            
        except ValueError:
            await update.message.reply_text(
                "Invalid discount amount! Please enter a number.",
                reply_markup=create_reply_markup([["0", "50", "100"], [Buttons.CANCEL]])
            )
            return CONFIRM_BILL

    @staticmethod
    async def cancel_billing(update: Update, context: CallbackContext):
        """Cancel the billing process"""
        if 'bill' in context.user_data:
            # Restore stock for items already added
            for item in context.user_data['bill']['items']:
                DBOperations.update_stock(item['product_id'], -item['quantity'])
            
            context.user_data.pop('bill', None)
        
        await update.message.reply_text(
            "Bill cancelled.",
            reply_markup=create_reply_markup(Buttons.MAIN_MENU)
        )
        return ConversationHandler.END