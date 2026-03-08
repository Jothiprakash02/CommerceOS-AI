"""
Database migration script to add 'starred' column to product_analysis table.
Run this once to update existing databases.

Usage:
    python scripts/add_starred_column.py
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Import using importlib to avoid 'global' keyword issue
import importlib.util
spec = importlib.util.spec_from_file_location("config", "global/config.py")
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)
DATABASE_URL = config_module.DATABASE_URL

def add_starred_column():
    """Add starred column to product_analysis table if it doesn't exist"""
    
    # Extract database path from DATABASE_URL
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        # Handle relative paths
        if not os.path.isabs(db_path):
            # Make it relative to the project root
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.normpath(os.path.join(project_root, db_path))
    else:
        print(f"Error: Only SQLite databases are supported. Current: {DATABASE_URL}")
        return False
    
    print(f"Database path: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        print("Database will be created automatically when you run the application.")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(product_analysis)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'starred' in columns:
            print("✓ Column 'starred' already exists in product_analysis table")
            conn.close()
            return True
        
        # Add the column
        print("Adding 'starred' column to product_analysis table...")
        cursor.execute("""
            ALTER TABLE product_analysis 
            ADD COLUMN starred BOOLEAN DEFAULT 0 NOT NULL
        """)
        conn.commit()
        
        print("✓ Successfully added 'starred' column")
        print("✓ All existing records set to starred=False (0)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Error adding column: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Database Migration: Add 'starred' Column")
    print("=" * 60)
    print()
    
    success = add_starred_column()
    
    print()
    if success:
        print("Migration completed successfully!")
        print("You can now use the star/unstar feature in the History page.")
    else:
        print("Migration failed. Please check the error messages above.")
    
    print()
