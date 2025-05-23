from config.settings import Config

class Messages:
    WELCOME = f"Welcome to {Config.COMPANY_NAME} Retail System!"
    MENU_PROMPT = "Please select an option:"
    INVALID_INPUT = "⚠️ Invalid input. Please try again."
    
    # Billing
    ENTER_CUSTOMER_NAME = "Please enter customer name:"
    ENTER_PHONE = "Please enter customer phone (or type 'skip'):"
    
    # Inventory
    SELECT_CATEGORY = "Please select a category:"
    SELECT_PRODUCT = "Please select a product:"
    SELECT_SIZE = "Please select pack size:"
    ENTER_QUANTITY = "Please enter quantity:"
    
    # Errors
    DB_ERROR = "⚠️ Database error occurred. Please try again later."

class Buttons:
    MAIN_MENU = [
        ["💰 Generate Bill", "📦 Inventory"],
        ["📊 Reports", "⚙️ Settings"]
    ]
    
    BACK = "🔙 Back"
    CANCEL = "❌ Cancel"
    CONFIRM = "✅ Confirm"