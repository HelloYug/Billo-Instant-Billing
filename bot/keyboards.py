from telegram import ReplyKeyboardMarkup, KeyboardButton
from config.constants import Buttons

def create_reply_markup(button_rows, resize=True, one_time=False):
    """
    Create a reply keyboard markup from button rows
    
    Args:
        button_rows: List of lists of button texts
        resize: Whether to resize keyboard
        one_time: Whether to hide after selection
    """
    keyboard = []
    for row in button_rows:
        keyboard.append([KeyboardButton(btn) for btn in row])
    
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=resize,
        one_time_keyboard=one_time
    )

def create_inline_keyboard(button_rows):
    """
    Create an inline keyboard from button rows
    
    Args:
        button_rows: List of lists of (text, callback_data) tuples
    """
    keyboard = []
    for row in button_rows:
        keyboard.append([InlineKeyboardButton(text, callback_data=data) for text, data in row])
    
    return InlineKeyboardMarkup(keyboard)

def get_back_button():
    """Return a back button keyboard"""
    return create_reply_markup([[Buttons.BACK]])