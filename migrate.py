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