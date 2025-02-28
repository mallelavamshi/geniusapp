#!/usr/bin/env python3
"""
Create First Admin User Script

This script creates the first administrator account in the system.
Use this when setting up the application for the first time.
"""

import sqlite3
import os
import sys
import getpass
from pathlib import Path

# Determine the database path - same logic as in config.py
DATABASE_PATH = "image_app.db"

def create_admin_user(username, password):
    """Create a new admin user in the database"""
    # Check if database exists
    if not os.path.exists(DATABASE_PATH):
        print(f"Error: Database file '{DATABASE_PATH}' not found.")
        print("Please run the application at least once to initialize the database.")
        return False
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    try:
        # Check if users table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not c.fetchone():
            print("Error: Users table does not exist in the database.")
            print("Please run the application at least once to initialize the database.")
            return False
        
        # Check if the username already exists
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        if c.fetchone():
            print(f"Error: Username '{username}' already exists.")
            return False
        
        # Get default user quota from settings
        c.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'default_user_quota'")
        result = c.fetchone()
        default_quota = int(result[0]) if result else 100
        
        # Insert the admin user
        c.execute(
            "INSERT INTO users (username, password, image_quota, images_processed, is_admin) VALUES (?, ?, ?, ?, ?)",
            (username, password, default_quota, 0, 1)
        )
        
        conn.commit()
        print(f"Admin user '{username}' created successfully!")
        return True
    
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("Create First Admin User")
    print("=======================")
    print()
    
    # Get username and password
    username = input("Enter admin username: ")
    password = getpass.getpass("Enter admin password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if not username:
        print("Error: Username cannot be empty.")
        sys.exit(1)
    
    if not password:
        print("Error: Password cannot be empty.")
        sys.exit(1)
    
    if password != confirm_password:
        print("Error: Passwords do not match.")
        sys.exit(1)
    
    # Create the admin user
    if create_admin_user(username, password):
        print()
        print("Done! You can now log in to the application with this admin account.")
    else:
        print()
        print("Failed to create admin user. Please check the errors above.")
        sys.exit(1)