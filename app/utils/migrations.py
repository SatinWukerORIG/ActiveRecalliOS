"""
Database migration utilities for Active Recall
"""
import sqlite3
import os
from datetime import datetime

class DatabaseMigrator:
    """Handle database schema migrations"""
    
    def __init__(self, db_path='instance/active_recall.db'):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        if not os.path.exists(self.db_path):
            raise Exception(f"Database not found at {self.db_path}")
        return sqlite3.connect(self.db_path)
    
    def column_exists(self, table_name, column_name):
        """Check if a column exists in a table"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        
        conn.close()
        return column_name in columns
    
    def add_column(self, table_name, column_name, column_type, default_value=None):
        """Add a column to a table"""
        if self.column_exists(table_name, column_name):
            print(f"Column '{column_name}' already exists in table '{table_name}'")
            return True
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Build ALTER TABLE statement
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            if default_value is not None:
                if isinstance(default_value, str):
                    alter_sql += f" DEFAULT '{default_value}'"
                else:
                    alter_sql += f" DEFAULT {default_value}"
            
            cursor.execute(alter_sql)
            conn.commit()
            conn.close()
            
            print(f"Successfully added column '{column_name}' to table '{table_name}'")
            return True
            
        except Exception as e:
            print(f"Failed to add column '{column_name}' to table '{table_name}': {e}")
            return False
    
    def run_migration(self, migration_name, migration_func):
        """Run a migration with logging"""
        print(f"\n🔄 Running migration: {migration_name}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            success = migration_func()
            if success:
                print(f"✅ Migration '{migration_name}' completed successfully!")
            else:
                print(f"❌ Migration '{migration_name}' failed!")
            return success
        except Exception as e:
            print(f"❌ Migration '{migration_name}' failed with error: {e}")
            return False

def migrate_add_recall_paused():
    """Migration: Add recall_paused column to User table"""
    migrator = DatabaseMigrator()
    return migrator.add_column('user', 'recall_paused', 'BOOLEAN', 0)

def migrate_add_folders():
    """Migration: Add Folder table and folder_id to Card table"""
    migrator = DatabaseMigrator()
    
    # Add folder_id column to Card table
    success1 = migrator.add_column('card', 'folder_id', 'INTEGER', None)
    
    # Note: SQLite doesn't support adding foreign key constraints to existing tables
    # The Folder table will be created automatically by SQLAlchemy when the app starts
    
    return success1

def migrate_add_recall_folders():
    """Migration: Add recall_folders column to User table"""
    migrator = DatabaseMigrator()
    return migrator.add_column('user', 'recall_folders', 'TEXT', None)

def migrate_add_parent_folder_id():
    """Migration: Add parent_folder_id column to Folder table for hierarchical folders"""
    migrator = DatabaseMigrator()
    return migrator.add_column('folder', 'parent_folder_id', 'INTEGER', None)

def run_all_migrations():
    """Run all pending migrations"""
    migrator = DatabaseMigrator()
    
    migrations = [
        ("Add recall_paused column", migrate_add_recall_paused),
        ("Add folder support", migrate_add_folders),
        ("Add recall_folders column", migrate_add_recall_folders),
        ("Add parent_folder_id for hierarchical folders", migrate_add_parent_folder_id),
        # Add future migrations here
    ]
    
    print("🚀 Starting database migrations...")
    
    all_successful = True
    for migration_name, migration_func in migrations:
        success = migrator.run_migration(migration_name, migration_func)
        if not success:
            all_successful = False
    
    if all_successful:
        print("\n🎉 All migrations completed successfully!")
    else:
        print("\n⚠️  Some migrations failed. Please check the logs above.")
    
    return all_successful

if __name__ == '__main__':
    run_all_migrations()