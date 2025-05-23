def validate_quantity(input_str):
    """Validate quantity input"""
    try:
        quantity = int(input_str)
        return quantity > 0
    except ValueError:
        return False

def validate_price(input_str):
    """Validate price input"""
    try:
        price = float(input_str)
        return price >= 0
    except ValueError:
        return False

def validate_date(date_str):
    """Validate date input (YYYY-MM-DD)"""
    from datetime import datetime
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False