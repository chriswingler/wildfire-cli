import aiosqlite
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATABASE_PATH = './db/moderation.db'

async def get_db_connection():
    """
    Connects to the SQLite database. Creates the database file and directory if they don't exist.
    Returns the connection object.
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        db = await aiosqlite.connect(DATABASE_PATH)
        logging.info(f"Successfully connected to the database: {DATABASE_PATH}")
        return db
    except aiosqlite.Error as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

async def create_tables(db):
    """
    Creates the necessary tables in the database if they don't already exist.
    """
    try:
        cursor = await db.cursor()

        # Create warnings table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS warnings (
                warning_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                rule_id TEXT,
                severity TEXT NOT NULL,
                reason TEXT,
                moderator_id INTEGER,
                action_taken TEXT
            )
        ''')
        logging.info("Checked/created 'warnings' table.")

        # Create appeals table
        # Create appeals table - MODIFIED
        # Removed FOREIGN KEY constraint to allow appealing various action_ids from action_logs
        # Changed action_id to action_id_appealed and type to TEXT
        # Added original_action_type and appeal_submission_log_id
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS appeals (
                appeal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                action_id_appealed TEXT NOT NULL,
                original_action_type TEXT,
                reason TEXT NOT NULL,
                status TEXT DEFAULT 'PENDING',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                moderator_id INTEGER,
                appeal_decision_timestamp DATETIME,
                appeal_submission_log_id TEXT
            )
        ''')
        logging.info("Checked/created 'appeals' table (schema updated).")

        # Create action_logs table
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id TEXT UNIQUE NOT NULL,
                guild_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER NOT NULL,
                target_user_id INTEGER,
                action_type TEXT NOT NULL,
                reason TEXT,
                moderator_id INTEGER,
                channel_id INTEGER,
                message_id INTEGER,
                duration_seconds INTEGER
            )
        ''')
        logging.info("Checked/created 'action_logs' table.")

        await db.commit()
        logging.info("All tables checked/created successfully.")
    except aiosqlite.Error as e:
        logging.error(f"Error creating tables: {e}")
        await db.rollback() # Rollback changes if an error occurs
        raise
    finally:
        if cursor:
            await cursor.close()

async def main():
    """Main function to test database connection and table creation."""
    db = None
    try:
        db = await get_db_connection()
        await create_tables(db)
    except Exception as e:
        logging.error(f"An error occurred in the main execution: {e}")
    finally:
        if db:
            await db.close()
            logging.info("Database connection closed.")

if __name__ == '__main__':
    # This is just for testing the script directly.
    # In a real application, you'd import and call these functions as needed.
    import asyncio
    asyncio.run(main())
