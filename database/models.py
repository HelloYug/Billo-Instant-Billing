from .connection import db
from config.settings import Config

class DBInitializer:
    @staticmethod
    def initialize_database():
        # Create tables if they don't exist
        db.execute_query("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2) NOT NULL,
            cost DECIMAL(10, 2) NOT NULL,
            stock INT NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        
        db.execute_query("""
        CREATE TABLE IF NOT EXISTS bills (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bill_number VARCHAR(20) UNIQUE NOT NULL,
            customer_name VARCHAR(100) NOT NULL,
            customer_phone VARCHAR(20),
            total_amount DECIMAL(12, 2) NOT NULL,
            discount DECIMAL(10, 2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        db.execute_query("""
        CREATE TABLE IF NOT EXISTS bill_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bill_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            unit_price DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (bill_id) REFERENCES bills(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        """)
        
        # Generate unique bill number sequence
        db.execute_query("""
        CREATE TABLE IF NOT EXISTS sequences (
            name VARCHAR(50) PRIMARY KEY,
            value INT NOT NULL DEFAULT 1
        )
        """)
        
        # Insert default sequence if not exists
        db.execute_query("""
        INSERT IGNORE INTO sequences (name, value) VALUES ('bill_sequence', 1)
        """)

# Initialize database on import
DBInitializer.initialize_database()