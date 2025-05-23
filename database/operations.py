from .connection import db
from config.settings import Config

class DBOperations:
    @staticmethod
    def get_categories():
        return db.execute_query("SELECT DISTINCT category FROM products ORDER BY category")
    
    @staticmethod
    def get_products_by_category(category):
        return db.execute_query(
            "SELECT id, name FROM products WHERE category = %s ORDER BY name",
            (category,)
        )
    
    @staticmethod
    def get_product_details(product_id):
        return db.execute_query(
            "SELECT * FROM products WHERE id = %s",
            (product_id,)
        )
    
    @staticmethod
    def update_stock(product_id, quantity):
        return db.execute_query(
            "UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s",
            (quantity, product_id, quantity)
        )
    
    @staticmethod
    def create_bill(customer_name, customer_phone, items):
        # First create bill record
        bill_id = db.execute_query(
            "INSERT INTO bills (customer_name, customer_phone) VALUES (%s, %s)",
            (customer_name, customer_phone if customer_phone != 'skip' else None)
        )
        
        # Then add bill items
        for item in items:
            db.execute_query(
                "INSERT INTO bill_items (bill_id, product_id, quantity, unit_price) "
                "VALUES (%s, %s, %s, %s)",
                (bill_id, item['product_id'], item['quantity'], item['price'])
            )
        
        return bill_id