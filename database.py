import sqlite3
from datetime import datetime
import pandas as pd
import os
import logging

# Import configuration
import config

# Get logger
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    # Create users table with quota field
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        image_quota INTEGER DEFAULT 100,
        images_processed INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0
    )
    ''')
    
    # Create system_settings table for global configurations
    c.execute('''
    CREATE TABLE IF NOT EXISTS system_settings (
        setting_key TEXT PRIMARY KEY,
        setting_value TEXT,
        description TEXT
    )
    ''')
    
    # Create tasks table with ability to cancel
    c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task_type TEXT NOT NULL,
        task_name TEXT,
        task_description TEXT,
        status TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL,
        completed_at TIMESTAMP,
        output_path TEXT,
        is_cancelled INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create images table
    c.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        image_path TEXT NOT NULL,
        imgbb_url TEXT,
        description TEXT,
        analysis TEXT,
        is_processed INTEGER DEFAULT 0,
        FOREIGN KEY (task_id) REFERENCES tasks (id)
    )
    ''')
    
    # Insert default settings if they don't exist
    c.execute("SELECT COUNT(*) FROM system_settings WHERE setting_key = 'max_bulk_upload'")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO system_settings (setting_key, setting_value, description) VALUES (?, ?, ?)",
            ('max_bulk_upload', '25', 'Maximum number of images allowed in a single bulk upload')
        )
    
    c.execute("SELECT COUNT(*) FROM system_settings WHERE setting_key = 'default_user_quota'")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO system_settings (setting_key, setting_value, description) VALUES (?, ?, ?)",
            ('default_user_quota', '100', 'Default image quota for new users')
        )
    
    conn.commit()
    conn.close()

def migrate_db():
    """Migrate existing database to new schema if needed"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    try:
        # Check if columns already exist in users table
        c.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'image_quota' not in columns:
            c.execute("ALTER TABLE users ADD COLUMN image_quota INTEGER DEFAULT 100")
            logger.info("Added image_quota column to users table")
        
        if 'images_processed' not in columns:
            c.execute("ALTER TABLE users ADD COLUMN images_processed INTEGER DEFAULT 0")
            logger.info("Added images_processed column to users table")
        
        if 'is_admin' not in columns:
            c.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
            logger.info("Added is_admin column to users table")
        
        # Check if columns already exist in tasks table
        c.execute("PRAGMA table_info(tasks)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'task_name' not in columns:
            c.execute("ALTER TABLE tasks ADD COLUMN task_name TEXT")
            logger.info("Added task_name column to tasks table")
        
        if 'task_description' not in columns:
            c.execute("ALTER TABLE tasks ADD COLUMN task_description TEXT")
            logger.info("Added task_description column to tasks table")
        
        if 'is_cancelled' not in columns:
            c.execute("ALTER TABLE tasks ADD COLUMN is_cancelled INTEGER DEFAULT 0")
            logger.info("Added is_cancelled column to tasks table")
        
        # Check if columns already exist in images table
        c.execute("PRAGMA table_info(images)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'is_processed' not in columns:
            c.execute("ALTER TABLE images ADD COLUMN is_processed INTEGER DEFAULT 0")
            logger.info("Added is_processed column to images table")
        
        # Check if system_settings table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_settings'")
        if not c.fetchone():
            c.execute('''
            CREATE TABLE system_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT,
                description TEXT
            )
            ''')
            logger.info("Created system_settings table")
            
            # Insert default settings
            c.execute(
                "INSERT INTO system_settings (setting_key, setting_value, description) VALUES (?, ?, ?)",
                ('max_bulk_upload', '25', 'Maximum number of images allowed in a single bulk upload')
            )
            c.execute(
                "INSERT INTO system_settings (setting_key, setting_value, description) VALUES (?, ?, ?)",
                ('default_user_quota', '100', 'Default image quota for new users')
            )
            logger.info("Added default system settings")
        
        conn.commit()
        logger.info("Database migration successful")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error during migration: {e}")
    finally:
        conn.close()

def create_user(username, password, is_admin=False):
    """Create a new user in the database"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    # Get default user quota from settings
    c.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'default_user_quota'")
    result = c.fetchone()
    default_quota = int(result[0]) if result else 100
    
    try:
        c.execute(
            "INSERT INTO users (username, password, image_quota, images_processed, is_admin) VALUES (?, ?, ?, ?, ?)", 
            (username, password, default_quota, 0, 1 if is_admin else 0)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    """Authenticate a user and return user ID if successful"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_info(user_id):
    """Get user information including quota and usage"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("SELECT username, image_quota, images_processed FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return {
            "username": result[0],
            "image_quota": result[1],
            "images_processed": result[2],
            "remaining_quota": result[1] - result[2]
        }
    return None


def is_admin(user_id):
    """Check if a user is an admin"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return result[0] == 1
    return False

def set_admin_status(user_id, is_admin_value):
    """Set a user's admin status"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute("UPDATE users SET is_admin = ? WHERE id = ?", (1 if is_admin_value else 0, user_id))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error setting admin status: {e}")
        return False
    finally:
        conn.close()

def get_user_info(user_id):
    """Get user information including quota, usage and admin status"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("SELECT username, image_quota, images_processed, is_admin FROM users WHERE id = ?", (user_id,))
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return {
            "username": result[0],
            "image_quota": result[1],
            "images_processed": result[2],
            "remaining_quota": result[1] - result[2],
            "is_admin": result[3] == 1
        }
    return None

def update_user_quota(user_id, new_quota):
    """Update a user's image quota"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute("UPDATE users SET image_quota = ? WHERE id = ?", (new_quota, user_id))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating user quota: {e}")
        return False
    finally:
        conn.close()

def reset_user_usage(user_id):
    """Reset a user's processed images count"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute("UPDATE users SET images_processed = 0 WHERE id = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error resetting user usage: {e}")
        return False
    finally:
        conn.close()

def increment_user_processed_images(user_id, count=1):
    """Increment the number of images a user has processed"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute("UPDATE users SET images_processed = images_processed + ? WHERE id = ?", (count, user_id))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error incrementing processed images: {e}")
        return False
    finally:
        conn.close()

def get_system_setting(setting_key, default_value=None):
    """Get a system setting value"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("SELECT setting_value FROM system_settings WHERE setting_key = ?", (setting_key,))
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return result[0]
    return default_value

def update_system_setting(setting_key, setting_value, description=None):
    """Update a system setting"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    try:
        # Check if setting exists
        c.execute("SELECT COUNT(*) FROM system_settings WHERE setting_key = ?", (setting_key,))
        if c.fetchone()[0] > 0:
            if description:
                c.execute(
                    "UPDATE system_settings SET setting_value = ?, description = ? WHERE setting_key = ?", 
                    (setting_value, description, setting_key)
                )
            else:
                c.execute(
                    "UPDATE system_settings SET setting_value = ? WHERE setting_key = ?", 
                    (setting_value, setting_key)
                )
        else:
            c.execute(
                "INSERT INTO system_settings (setting_key, setting_value, description) VALUES (?, ?, ?)",
                (setting_key, setting_value, description or "")
            )
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error updating system setting: {e}")
        return False
    finally:
        conn.close()

def create_new_task(user_id, task_type, task_name="", task_description=""):
    """Create a new task in the database and return its ID"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute(
        "INSERT INTO tasks (user_id, task_type, task_name, task_description, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, task_type, task_name, task_description, 'pending', current_time)
    )
    
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return task_id

def add_image_to_task(task_id, image_path, description=""):
    """Add an image to a task"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    c.execute(
        "INSERT INTO images (task_id, image_path, description, is_processed) VALUES (?, ?, ?, ?)",
        (task_id, image_path, description, 0)
    )
    
    image_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return image_id

def update_image_with_imgbb_url(image_id, imgbb_url):
    """Update image record with ImgBB URL"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("UPDATE images SET imgbb_url = ? WHERE id = ?", (imgbb_url, image_id))
    
    conn.commit()
    conn.close()

def update_image_with_analysis(image_id, analysis):
    """Update image record with analysis results and mark as processed"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    # Make sure analysis is a string
    if not isinstance(analysis, str):
        analysis = str(analysis)
    
    c.execute("UPDATE images SET analysis = ?, is_processed = 1 WHERE id = ?", (analysis, image_id))
    
    conn.commit()
    conn.close()

def cancel_task(task_id):
    """Mark a task as cancelled"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    try:
        c.execute("UPDATE tasks SET is_cancelled = 1 WHERE id = ?", (task_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error cancelling task: {e}")
        return False
    finally:
        conn.close()

def is_task_cancelled(task_id):
    """Check if a task has been cancelled"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("SELECT is_cancelled FROM tasks WHERE id = ?", (task_id,))
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return result[0] == 1
    return False

def update_task_status(task_id, status, output_path=None):
    """Update task status and output path if completed"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    if status == 'completed':
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute(
            "UPDATE tasks SET status = ?, completed_at = ?, output_path = ? WHERE id = ?", 
            (status, current_time, output_path, task_id)
        )
    else:
        c.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    
    conn.commit()
    conn.close()

def manually_complete_task(task_id, output_path=None):
    """Manually mark a task as completed"""
    return update_task_status(task_id, 'completed', output_path)

def get_task_images(task_id):
    """Get all images for a specific task"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    
    images = pd.read_sql_query(
        "SELECT id, image_path, description, imgbb_url, analysis, is_processed FROM images WHERE task_id = ?",
        conn,
        params=(task_id,)
    )
    
    conn.close()
    
    return images

def get_task_status(task_id):
    """Get the current status of a task"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
    result = c.fetchone()
    
    conn.close()
    
    return result[0] if result else None

def get_task_type(task_id):
    """Get the type of a task (bulk or single)"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("SELECT task_type FROM tasks WHERE id = ?", (task_id,))
    result = c.fetchone()
    
    conn.close()
    
    return result[0] if result else None

def get_task_owner(task_id):
    """Get the user ID of the task owner"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    c.execute("SELECT user_id FROM tasks WHERE id = ?", (task_id,))
    result = c.fetchone()
    
    conn.close()
    
    return result[0] if result else None

def get_user_tasks(user_id):
    """Get all tasks for a specific user with image count and task name"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    
    # Check if columns exist for backward compatibility
    c = conn.cursor()
    c.execute("PRAGMA table_info(tasks)")
    columns = [column[1] for column in c.fetchall()]
    
    if all(col in columns for col in ['task_name', 'task_description']):
        tasks_df = pd.read_sql_query(
            """
            SELECT t.id, t.task_type, t.task_name, t.task_description, t.status, 
                   t.created_at, t.completed_at, t.output_path, t.is_cancelled,
                   COUNT(i.id) as image_count,
                   SUM(CASE WHEN i.is_processed = 1 THEN 1 ELSE 0 END) as processed_count
            FROM tasks t
            LEFT JOIN images i ON t.id = i.task_id
            WHERE t.user_id = ?
            GROUP BY t.id
            ORDER BY t.created_at DESC
            """,
            conn,
            params=(user_id,)
        )
    else:
        tasks_df = pd.read_sql_query(
            """
            SELECT t.id, t.task_type, t.status, t.created_at, t.completed_at, t.output_path,
                   COUNT(i.id) as image_count
            FROM tasks t
            LEFT JOIN images i ON t.id = i.task_id
            WHERE t.user_id = ?
            GROUP BY t.id
            ORDER BY t.created_at DESC
            """,
            conn,
            params=(user_id,)
        )
        # Add empty columns for compatibility
        tasks_df['task_name'] = ""
        tasks_df['task_description'] = ""
        tasks_df['is_cancelled'] = 0
        tasks_df['processed_count'] = 0
    
    conn.close()
    
    return tasks_df

def get_image_analysis(task_id):
    """Get analysis results for all images in a task"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    
    images_df = pd.read_sql_query(
        "SELECT image_path, description, analysis, is_processed FROM images WHERE task_id = ?",
        conn,
        params=(task_id,)
    )
    
    conn.close()
    
    return images_df

def delete_task(task_id):
    """Delete a task and all associated data"""
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    
    try:
        # Get task information first (including output path)
        c.execute("SELECT output_path FROM tasks WHERE id = ?", (task_id,))
        task_data = c.fetchone()
        output_path = task_data[0] if task_data else None
        
        # Get all images for this task
        c.execute("SELECT image_path FROM images WHERE task_id = ?", (task_id,))
        image_paths = [row[0] for row in c.fetchall()]
        
        # Delete images from database
        c.execute("DELETE FROM images WHERE task_id = ?", (task_id,))
        
        # Delete task from database
        c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        
        conn.commit()
        
        # Delete files from filesystem
        for image_path in image_paths:
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                logger.error(f"Error deleting image file {image_path}: {e}")
        
        # Delete output file if exists
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
            except Exception as e:
                logger.error(f"Error deleting output file {output_path}: {e}")
                
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting task: {e}")
        return False
    finally:
        conn.close()

def has_remaining_quota(user_id):
    """Check if a user has remaining quota"""
    user_info = get_user_info(user_id)
    if user_info:
        return user_info["remaining_quota"] > 0
    return False

def check_bulk_upload_limit(count):
    """Check if the number of images is within the bulk upload limit"""
    max_bulk = int(get_system_setting('max_bulk_upload', 25))
    return count <= max_bulk

def get_bulk_upload_limit():
    """Get the maximum number of images allowed in a bulk upload"""
    return int(get_system_setting('max_bulk_upload', 25))