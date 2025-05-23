"""
BillO Telegram Bot Package

This package contains all the Telegram bot components for the BillO Instant Billing system.
It provides a complete retail management solution with billing, inventory, and customer management.

Modules:
    - main: The main bot entry point and setup
    - handlers: All conversation handlers for different features
    - keyboards: Keyboard layouts and markup generators
"""

from .main import RetailBot
from .handlers import billing, inventory, customer
from .keyboards import create_reply_markup, create_inline_keyboard, get_back_button

__all__ = [
    'RetailBot',
    'billing',
    'inventory',
    'customer',
    'create_reply_markup',
    'create_inline_keyboard',
    'get_back_button'
]

__version__ = '1.0.0'
__author__ = 'Yug Agarwal'
__license__ = 'MIT'