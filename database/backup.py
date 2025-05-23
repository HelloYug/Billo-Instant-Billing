import os
import datetime
from .connection import db
from config.settings import Config

class BackupManager:
    BACKUP_DIR = os.path.join(os.path.dirname(__file__), '../../data/backups')
    
    @staticmethod
    def create_backup():
        if not os.path.exists(BackupManager.BACKUP_DIR):
            os.makedirs(BackupManager.BACKUP_DIR)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BackupManager.BACKUP_DIR, f"backup_{timestamp}.sql")
        
        try:
            # Get all tables
            tables = db.execute_query("SHOW TABLES")
            
            with open(backup_file, 'w') as f:
                for table in tables:
                    table_name = table[f"Tables_in_{Config.DB_CONFIG['database']}"]
                    
                    # Get create table statement
                    create_table = db.execute_query(f"SHOW CREATE TABLE {table_name}")[0]['Create Table']
                    f.write(f"{create_table};\n\n")
                    
                    # Get table data
                    rows = db.execute_query(f"SELECT * FROM {table_name}")
                    if rows:
                        columns = list(rows[0].keys())
                        for row in rows:
                            values = []
                            for col in columns:
                                val = row[col]
                                if val is None:
                                    values.append("NULL")
                                elif isinstance(val, (int, float)):
                                    values.append(str(val))
                                else:
                                    values.append(f"'{str(val).replace("'", "''")}'")
                            
                            f.write(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
                        f.write("\n")
            
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False