import discord
import asyncio
import aiosqlite
from typing import List # Added for type hinting

class MessageIndexer:
    def __init__(self, bot, db_path, skipped_channel_ids: List[str], incremental_index_delay_seconds: int = 3600):
        self.bot = bot
        self.db_path = db_path
        self.batch_size = 100
        self.incremental_index_delay_seconds = incremental_index_delay_seconds
        self.incremental_indexing_task = None
        self._stop_event = asyncio.Event()
        self.skipped_channel_ids = set(skipped_channel_ids) # Store as a set for efficient lookup

    async def initialize_database(self):
        """Initializes the database and creates the message_index table if it doesn't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS message_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE NOT NULL,
                    guild_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    author_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("CREATE INDEX IF NOT EXISTS idx_message_content ON message_index(content)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_message_timestamp ON message_index(timestamp)")
            await db.commit()

    async def index_message(self, message: discord.Message):
        """Indexes a single message."""
        if message.author.bot:  # Ignore messages from bots
            return

        # Privacy: Check if channel is skipped
        if message.guild and str(message.channel.id) in self.skipped_channel_ids:
            # print(f"Skipping message from {message.channel.id} as it's in skipped channels list.")
            return

        sanitized_content = self.sanitize_content(message.content)
        if not sanitized_content:  # Ignore empty messages after sanitization
            return

        # TODO: Implement privacy filtering for sensitive channels (this check is a good start)

        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT INTO message_index (message_id, guild_id, channel_id, author_id, content, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    str(message.id),
                    str(message.guild.id),
                    str(message.channel.id),
                    str(message.author.id),
                    sanitized_content,
                    message.created_at.isoformat()
                ))
                await db.commit()
                print(f"Indexed message: {message.id}")
            except aiosqlite.IntegrityError:
                print(f"Message {message.id} already indexed.") # Or handle as an update
            except Exception as e:
                print(f"Error indexing message {message.id}: {e}")

    def sanitize_content(self, content: str) -> str:
        """Sanitizes message content.
        - Removes leading/trailing whitespace
        - Placeholder for more complex sanitization (e.g., removing PII)
        """
        return content.strip()

    async def batch_index_historical_messages(self, channel: discord.TextChannel, limit: int = 1000):
        """Indexes historical messages from a channel in batches."""
        # Privacy: Check if channel is skipped
        if str(channel.id) in self.skipped_channel_ids:
            print(f"Skipping historical indexing for channel {channel.name} ({channel.id}) as it's in skipped list.")
            return

        # TODO: Implement privacy filtering for sensitive channels before processing history (this check is a good start)
        print(f"Starting historical message indexing for channel {channel.name} ({channel.id}).") # Added print
        count = 0
        async for message in channel.history(limit=limit, oldest_first=True):
            if message.author.bot:
                continue
            await self.index_message(message)
            count += 1
            if count % self.batch_size == 0:
                print(f"Processed {count} historical messages from {channel.name}...")
        print(f"Finished indexing {count} historical messages from {channel.name}.")

    async def on_message(self, message: discord.Message):
        """Event handler for new messages."""
        # This will be connected to the bot's on_message event
        await self.index_message(message)

    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Event handler for edited messages."""
        # Re-index the edited message
        await self.index_message(after)

    async def on_message_delete(self, message: discord.Message):
        """Event handler for deleted messages."""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("DELETE FROM message_index WHERE message_id = ?", (str(message.id),))
                await db.commit()
                print(f"Deleted message from index: {message.id}")
            except Exception as e:
                print(f"Error deleting message {message.id} from index: {e}")

    async def get_latest_indexed_timestamp(self, channel_id: str = None) -> str | None:
        """Fetches the latest indexed message timestamp for a specific channel or globally."""
        async with aiosqlite.connect(self.db_path) as db:
            if channel_id:
                cursor = await db.execute(
                    "SELECT MAX(timestamp) FROM message_index WHERE channel_id = ?",
                    (channel_id,)
                )
            else:
                cursor = await db.execute("SELECT MAX(timestamp) FROM message_index")

            result = await cursor.fetchone()
            return result[0] if result and result[0] else None

    async def incremental_index_channel(self, channel: discord.TextChannel, after_timestamp_iso: str | None):
        """Indexes new messages in a channel after a given timestamp."""
        # Privacy: Check if channel is skipped
        if str(channel.id) in self.skipped_channel_ids:
            # print(f"Skipping incremental indexing for channel {channel.name} ({channel.id}) as it's in skipped list.")
            return 0 # Return 0 as no messages were indexed

        if not channel.permissions_for(channel.guild.me).read_message_history:
            print(f"No permission to read history in {channel.name} ({channel.id}). Skipping.")
            return 0

        # TODO: Implement privacy filtering for sensitive channels (check channel against a skip list) (this check is a good start)

        after_datetime = None
        if after_timestamp_iso:
            try:
                after_datetime = discord.utils.parse_time(after_timestamp_iso)
            except Exception: # Handles potential parsing errors if timestamp is malformed
                print(f"Warning: Could not parse timestamp {after_timestamp_iso} for channel {channel.id}")
                # Decide on fallback: re-index all, or skip this run for this channel
                # For now, let's proceed as if no timestamp was found, potentially re-indexing more than necessary
                # but avoiding a crash. A safer bet might be to return 0 here.
                pass # Or set after_datetime to None explicitly to fetch from beginning (if desired)

        count = 0
        # Fetch messages after the specific datetime object
        # The 'after' parameter in channel.history expects a datetime object
        async for message in channel.history(limit=None, after=after_datetime, oldest_first=True):
            if message.author.bot:
                continue

            # Small delay to avoid hitting rate limits aggressively during scans
            await asyncio.sleep(0.1) # 100ms delay between processing each message in history scan

            await self.index_message(message) # index_message already handles duplicates
            count += 1
            if count % self.batch_size == 0:
                print(f"Incrementally processed {count} messages from {channel.name}...")

        if count > 0:
            print(f"Incrementally indexed {count} new messages from {channel.name}.")
        return count

    async def run_incremental_indexing(self):
        """Periodically scans all accessible channels for new messages and indexes them."""
        await self.bot.wait_until_ready() # Ensure bot is fully ready

        while not self._stop_event.is_set():
            print(f"Starting incremental indexing cycle at {discord.utils.utcnow()}...")
            total_indexed_this_cycle = 0

            latest_global_timestamp = await self.get_latest_indexed_timestamp()
            # If no messages ever indexed, latest_global_timestamp will be None.
            # channel.history(after=None) fetches from the beginning.
            # This is okay for the first run, but could be optimized to fetch only last N days if DB is empty.

            for guild in self.bot.guilds:
                for channel in guild.text_channels:
                    if self._stop_event.is_set():
                        print("Incremental indexing stop event received during channel scan.")
                        return

                    # Instead of per-channel timestamp, we can use global or per-guild for simplicity,
                    # or fetch per-channel if more granularity is needed.
                    # For now, using latest_global_timestamp as a general "after" mark.
                    # A more robust approach might be to track last indexed message per channel.
                    # However, `index_message` handles duplicates, so re-processing is not catastrophic, just inefficient.

                    # For this implementation, let's try per-channel last message for better efficiency
                    latest_channel_timestamp = await self.get_latest_indexed_timestamp(channel_id=str(channel.id))

                    try:
                        indexed_in_channel = await self.incremental_index_channel(channel, latest_channel_timestamp)
                        total_indexed_this_cycle += indexed_in_channel
                        # Optional: small delay between channels to further distribute load
                        await asyncio.sleep(1)
                    except discord.errors.Forbidden:
                        print(f"Forbidden to access channel {channel.name} in {guild.name}. Skipping.")
                    except Exception as e:
                        print(f"Error during incremental indexing of channel {channel.name}: {e}")

            print(f"Incremental indexing cycle finished. Indexed {total_indexed_this_cycle} new messages.")
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.incremental_index_delay_seconds)
            except asyncio.TimeoutError:
                pass # This is expected, loop continues
            except Exception as e:
                print(f"Error in incremental indexing wait: {e}")
                # If _stop_event.wait() itself errors, good to break or handle
                break
        print("Incremental indexing task has stopped.")

    def start_background_indexing(self):
        """Starts the incremental indexing background task."""
        if self.incremental_indexing_task is None or self.incremental_indexing_task.done():
            self._stop_event.clear()
            self.incremental_indexing_task = self.bot.loop.create_task(self.run_incremental_indexing())
            print("Incremental indexing background task started.")
        else:
            print("Incremental indexing task already running.")

    async def stop_background_indexing(self):
        """Stops the incremental indexing background task gracefully."""
        if self.incremental_indexing_task and not self.incremental_indexing_task.done():
            print("Stopping incremental indexing background task...")
            self._stop_event.set()
            try:
                await asyncio.wait_for(self.incremental_indexing_task, timeout=30.0) # Wait for task to finish
            except asyncio.TimeoutError:
                print("Incremental indexing task did not stop in time. Cancelling.")
                self.incremental_indexing_task.cancel()
            except Exception as e:
                print(f"Error during background task stop: {e}")
            finally:
                self.incremental_indexing_task = None
                print("Incremental indexing background task definitively stopped.")
        else:
            print("Incremental indexing background task not running or already stopped.")

async def setup_message_indexer(bot, db_path, skipped_channel_ids: List[str], incremental_index_delay_seconds: int = 3600):
    """Sets up the message indexer, connects its event handlers, and starts background tasks."""
    indexer = MessageIndexer(bot, db_path, skipped_channel_ids, incremental_index_delay_seconds)
    await indexer.initialize_database()

    bot.add_listener(indexer.on_message, 'on_message')
    bot.add_listener(indexer.on_message_edit, 'on_message_edit')
    bot.add_listener(indexer.on_message_delete, 'on_message_delete')

    indexer.start_background_indexing() # Start the background task

    print("Message Indexer setup complete and background indexing started.")
    return indexer
