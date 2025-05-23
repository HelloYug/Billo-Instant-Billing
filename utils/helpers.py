import datetime
from config.settings import Config

def generate_bill_number():
    """Generate a unique bill number"""
    today = datetime.datetime.now().strftime("%Y%m%d")
    sequence = DBOperations.get_next_sequence('bill_sequence')
    return f"{Config.BILL_PREFIX}-{today}-{sequence:04d}"

def format_currency(amount):
    """Format amount as currency"""
    return f"{Config.CURRENCY}{amount:,.2f}"

def validate_phone(phone):
    """Validate phone number format"""
    return phone.isdigit() and len(phone) == 10