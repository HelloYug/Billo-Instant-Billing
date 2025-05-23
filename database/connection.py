import mysql.connector
from mysql.connector import Error
from config.settings import Config

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._create_connection()
        return cls._instance
    
    def _create_connection(self):
        try:
            self.connection = mysql.connector.connect(
                **Config.DB_CONFIG,
                autocommit=True
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise
    
    def get_cursor(self):
        if not self.connection.is_connected():
            self._create_connection()
        return self.cursor
    
    def execute_query(self, query, params=None):
        try:
            cursor = self.get_cursor()
            cursor.execute(query, params or ())
            if query.strip().lower().startswith('select'):
                return cursor.fetchall()
            return True
        except Error as e:
            print(f"Database error: {e}")
            return False
    
    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()

# Singleton instance
db = DatabaseConnection()