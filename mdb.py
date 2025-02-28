#!/usr/bin/env python3
"""
Database Migration Script

This script updates an existing database to include new fields and tables
needed for the application's latest version.
"""

import sqlite3
import os
import sys

# Set the database path
DATABASE_PATH = "image_app.db"

def migrate_database():
    """Perform all necessary database migrations"""
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: Database file '{DATABASE_PATH}' not found.")
        return False
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        print("Starting database migration...")
        
        # --- Users Table Migrations ---
        print("Checking users table...")
        
        # Check if columns already exist in users table
        c.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in c.fetchall()]
        
        # Add image_quota if missing
        if 'image_quota' not in columns:
            print("Adding image_quota column to users table")
            c.execute("ALTER TABLE users ADD COLUMN image_quota INTEGER DEFAULT 100")
        
        # Add images_processed if missing
        if 'images_processed' not in columns:
            print("Adding images_processed column to users table")
            c.execute("ALTER TABLE users ADD COLUMN images_processed INTEGER DEFAULT 0")
        
        # Add is_admin if missing
        if 'is_admin' not in columns:
            print("Adding is_admin column to users table")
            c.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        
        # --- Tasks Table Migrations ---
        print("Checking tasks table...")
        
        # Check if tasks table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
        if not c.fetchone():
            print("Tasks table doesn't exist, skipping tasks migrations")
        else:
            # Check columns in tasks table
            c.execute("PRAGMA table_info(tasks)")
            columns = [column[1] for column in c.fetchall()]
            
            # Add task_name if missing
            if 'task_name' not in columns:
                print("Adding task_name column to tasks table")
                c.execute("ALTER TABLE tasks ADD COLUMN task_name TEXT")
            
            # Add task_description if missing
            if 'task_description' not in columns:
                print("Adding task_description column to tasks table")
                c.execute("ALTER TABLE tasks ADD COLUMN task_description TEXT")
            
            # Add is_cancelled if missing
            if 'is_cancelled' not in columns:
                print("Adding is_cancelled column to tasks table")
                c.execute("ALTER TABLE tasks ADD COLUMN is_cancelled INTEGER DEFAULT 0")
        
        # --- Images Table Migrations ---
        print("Checking images table...")
        
        # Check if images table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
        if not c.fetchone():
            print("Images table doesn't exist, skipping images migrations")
        else:
            # Check columns in images table
            c.execute("PRAGMA table_info(images)")
            columns = [column[1] for column in c.fetchall()]
            
            # Add is_processed if missing
            if 'is_processed' not in columns:
                print("Adding is_processed column to images table")
                c.execute("ALTER TABLE images ADD COLUMN is_processed INTEGER DEFAULT 0")
        
        # --- System Settings Table Creation ---
        print("Checking system_settings table...")
        
        # Check if system_settings table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_settings'")
        if not c.fetchone():
            print("Creating system_settings table")
            c.execute('''
            CREATE TABLE system_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT,
                description TEXT
            )
            ''')
            
            # Insert default settings
            c.execute(
                "INSERT INTO system_settings (setting_key, setting_value, description) VALUES (?, ?, ?)",
                ('max_bulk_upload', '25', 'Maximum number of images allowed in a single bulk upload')
            )
            c.execute(
                "INSERT INTO system_settings (setting_key, setting_value, description) VALUES (?, ?, ?)",
                ('default_user_quota', '100', 'Default image quota for new users')
            )
            print("Added default system settings")
        
        conn.commit()
        print("Database migration completed successfully!")
        return True
    
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("Database Migration Tool")
    print("======================")
    print()
    
    if migrate_database():
        print()
        print("Migration completed successfully!")
    else:
        print()
        print("Migration failed. Please check the errors above.")
        sys.exit(1)