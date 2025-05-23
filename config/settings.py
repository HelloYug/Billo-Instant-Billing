import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }
    
    # Telegram Configuration
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    
    # Business Configuration
    COMPANY_NAME = os.getenv('COMPANY_NAME')
    BILL_PREFIX = os.getenv('BILL_PREFIX')
    CURRENCY = os.getenv('CURRENCY')
    DEFAULT_DISCOUNT = float(os.getenv('DEFAULT_DISCOUNT'))