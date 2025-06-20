import aiosqlite
from typing import List, Dict, Any, Tuple
from nltk.tokenize import word_tokenize # Using nltk for tokenization
from thefuzz import fuzz # For fuzzy matching

# Ensure NLTK 'punkt' tokenizer models are downloaded.
# This typically should be handled during setup/deployment, not runtime in a module.
# For now, we'll assume it's available. Consider adding a check or note for deployment.
# try:
#     import nltk
#     nltk.data.find('tokenizers/punkt')
# except nltk.downloader.DownloadError:
#     nltk.download('punkt')

class SearchEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def simple_text_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Performs a simple keyword search using SQL LIKE.
        Returns a list of messages matching the query.
        """
        # Basic sanitization for the query
        sanitized_query = f"%{query.strip()}%"
        async with aiosqlite.connect(self.db_path) as db:
            # Using fts5 table if available would be better for performance
            # For now, using LIKE on the standard indexed content column
            cursor = await db.execute("""
                SELECT message_id, guild_id, channel_id, author_id, content, timestamp, created_at
                FROM message_index
                WHERE content LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (sanitized_query, limit))
            rows = await cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                "message_id": row[0],
                "guild_id": row[1],
                "channel_id": row[2],
                "author_id": row[3],
                "content": row[4],
                "timestamp": row[5],
                "created_at": row[6]
            })
        return results

    async def fuzzy_search(self, query: str, limit: int = 10, similarity_threshold: int = 70) -> List[Dict[str, Any]]:
        """Performs a fuzzy search on message content.
        Retrieves all messages and then filters by fuzzy similarity.
        NOTE: This is not efficient for large datasets. Consider FTS or other indexing for production.
        """
        query_tokens = self.preprocess_text(query)

        # In a real scenario, you'd fetch candidate messages more intelligently.
        # Fetching all messages is highly inefficient.
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT message_id, guild_id, channel_id, author_id, content, timestamp
                FROM message_index
                ORDER BY timestamp DESC
                LIMIT 10000 -- Arbitrary limit to prevent crashing on huge DBs
            """) # Consider limiting this further or using smarter pre-filtering
            all_messages = await cursor.fetchall()

        matches = []
        for msg_row in all_messages:
            message_content = msg_row[4]
            # Simple fuzzy match on the whole content.
            # More advanced would be to match on tokens or n-grams.
            ratio = fuzz.partial_ratio(query.lower(), message_content.lower())
            if ratio >= similarity_threshold:
                matches.append({
                    "message_id": msg_row[0],
                    "guild_id": msg_row[1],
                    "channel_id": msg_row[2],
                    "author_id": msg_row[3],
                    "content": message_content,
                    "timestamp": msg_row[5],
                    "similarity_score": ratio
                })

        # Sort by similarity, then by timestamp
        matches.sort(key=lambda x: (x['similarity_score'], x['timestamp']), reverse=True)
        return matches[:limit]

    def preprocess_text(self, text: str) -> List[str]:
        """Basic text preprocessing: lowercase and tokenize."""
        if not text:
            return []
        # Ensure NLTK punkt is available
        try:
            tokens = word_tokenize(text.lower())
            return tokens
        except LookupError:
            # This means 'punkt' is not downloaded.
            # In a real application, you'd handle this by either:
            # 1. Ensuring nltk.download('punkt') is run during setup.
            # 2. Logging an error and returning raw split or empty list.
            print("NLTK 'punkt' tokenizer model not found. Please download it by running: nltk.download('punkt')")
            # Fallback to simple split, though less effective
            return text.lower().split()


    async def semantic_search_preparation(self, query: str, documents: List[str]) -> Any:
        """Placeholder for semantic search preparation.
        This would involve generating embeddings for the query and documents.
        Requires a sentence transformer model or similar.
        """
        # Example:
        # model = SentenceTransformer('all-MiniLM-L6-v2')
        # query_embedding = model.encode(query)
        # document_embeddings = model.encode(documents)
        # return query_embedding, document_embeddings
        print("Semantic search preparation: Not implemented. Requires ML model.")
        return {"query": query, "status": "semantic search not implemented"}

    async def rank_results(self, results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Placeholder for result ranking.
        Could use factors like relevance, recency, author reputation, etc.
        For now, it just returns the results as is if no similarity score,
        or sorts by similarity if present.
        """
        if not results:
            return []

        if "similarity_score" in results[0]:
            # Already sorted by similarity in fuzzy_search
            return results
        elif "bm25_score" in results[0]: # Example for another scoring
            results.sort(key=lambda x: x["bm25_score"], reverse=True)
            return results

        # Default: if no specific score, assume already sorted (e.g., by time)
        print("Result ranking: Basic or no ranking applied.")
        return results

    async def paginate_results(self, results: List[Dict[str, Any]], page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Paginates the search results."""
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 10

        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        paginated_items = results[start_index:end_index]

        return {
            "page": page,
            "page_size": page_size,
            "total_results": len(results),
            "total_pages": (len(results) + page_size - 1) // page_size,
            "items": paginated_items
        }

    async def prepare_context_window(self, message_id: str, window_size_before: int = 5, window_size_after: int = 5) -> List[Dict[str, Any]]:
        """Prepares a context window of messages around a specific message_id.
        Fetches 'window_size_before' messages before and 'window_size_after' messages after the given message,
        from the same channel, ordered by timestamp.
        """
        async with aiosqlite.connect(self.db_path) as db:
            # Get the target message's timestamp and channel_id
            cursor = await db.execute("SELECT timestamp, channel_id FROM message_index WHERE message_id = ?", (message_id,))
            target_message_data = await cursor.fetchone()

            if not target_message_data:
                return [] # Target message not found

            target_timestamp, channel_id = target_message_data

            # Fetch messages before the target message
            cursor_before = await db.execute("""
                SELECT message_id, author_id, content, timestamp
                FROM message_index
                WHERE channel_id = ? AND timestamp < ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (channel_id, target_timestamp, window_size_before))
            messages_before = await cursor_before.fetchall()
            messages_before.reverse() # Order from oldest to newest

            # Fetch the target message itself
            cursor_target = await db.execute("""
                SELECT message_id, author_id, content, timestamp
                FROM message_index
                WHERE message_id = ?
            """, (message_id,))
            target_message = await cursor_target.fetchone()

            # Fetch messages after the target message
            cursor_after = await db.execute("""
                SELECT message_id, author_id, content, timestamp
                FROM message_index
                WHERE channel_id = ? AND timestamp > ?
                ORDER BY timestamp ASC
                LIMIT ?
            """, (channel_id, target_timestamp, window_size_after))
            messages_after = await cursor_after.fetchall()

        context_messages_raw = messages_before + ([target_message] if target_message else []) + messages_after

        context_messages_formatted = []
        for row in context_messages_raw:
            if row: # Ensure row is not None
                context_messages_formatted.append({
                    "message_id": row[0],
                    "author_id": row[1],
                    "content": row[2],
                    "timestamp": row[3]
                })
        return context_messages_formatted

# Example usage (for testing purposes, typically not run directly in the module)
async def main():
    # This requires a database wildfire_database.db with the message_index table
    # and some data to test against.
    # You would run this from a context where asyncio.run() is appropriate.

    # Create a dummy DB for testing if it doesn't exist
    DB_FOR_TESTING = "test_search_db.sqlite3"
    async with aiosqlite.connect(DB_FOR_TESTING) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS message_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT, message_id TEXT UNIQUE NOT NULL,
                guild_id TEXT NOT NULL, channel_id TEXT NOT NULL, author_id TEXT NOT NULL,
                content TEXT NOT NULL, timestamp DATETIME NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("CREATE INDEX IF NOT EXISTS idx_message_content ON message_index(content)")
        # Add some test data
        test_data = [
            ('msg1', 'guild1', 'chan1', 'user1', 'Hello world, this is a test message.', '2023-01-01T12:00:00'),
            ('msg2', 'guild1', 'chan1', 'user2', 'Another test message with world.', '2023-01-01T12:01:00'),
            ('msg3', 'guild1', 'chan1', 'user1', 'Fuzzy searching is fun.', '2023-01-01T12:02:00'),
            ('msg4', 'guild1', 'chan1', 'user3', 'This is about context window.', '2023-01-01T12:03:00'),
            ('msg5', 'guild1', 'chan1', 'user2', 'The message before the context target.', '2023-01-01T12:02:30'),
            ('msg6', 'guild1', 'chan1', 'user1', 'The message after the context target.', '2023-01-01T12:03:30'),
        ]
        try:
            await db.executemany("INSERT INTO message_index(message_id, guild_id, channel_id, author_id, content, timestamp) VALUES (?,?,?,?,?,?)", test_data)
            await db.commit()
        except aiosqlite.IntegrityError:
            print("Test data likely already exists.")

    engine = SearchEngine(DB_FOR_TESTING)

    print("--- Simple Text Search ---")
    results_simple = await engine.simple_text_search("test message")
    for res in results_simple:
        print(f"  Content: {res['content'][:50]}...")
    paginated_simple = await engine.paginate_results(results_simple, page=1, page_size=1)
    print(f"  Paginated: {paginated_simple}")

    print("\n--- Fuzzy Search ---")
    results_fuzzy = await engine.fuzzy_search("fuzzy serching", similarity_threshold=60) # Deliberate typo
    for res in results_fuzzy:
        print(f"  Content: {res['content'][:50]}... (Score: {res['similarity_score']})")

    print("\n--- Context Window Preparation ---")
    # Assuming 'msg4' is our target message for context
    context = await engine.prepare_context_window(message_id='msg4', window_size_before=2, window_size_after=2)
    if context:
        print(f"  Context for 'msg4' (target message content: '{context[len(context)//2]['content']}'):")
        for msg_ctx in context:
            print(f"    Ctx Content: {msg_ctx['content'][:50]}... (Timestamp: {msg_ctx['timestamp']})")
    else:
        print("  Could not retrieve context for 'msg4'.")

    print("\n--- Semantic Search (Placeholder) ---")
    semantic_prep = await engine.semantic_search_preparation("test query", ["doc1", "doc2"])
    print(f"  {semantic_prep}")

if __name__ == "__main__":
    # This is a common way to run async main for testing, but ensure it's suitable for your environment
    # For example, if running in a Jupyter notebook, you might use `await main()` directly if top-level await is enabled.
    # If this script is meant to be a module, this __main__ block is usually for testing only.
    # import asyncio
    # asyncio.run(main())
    print("SearchEngine module loaded. To test, uncomment asyncio.run(main()) and run as script, ensuring test_search_db.sqlite3 can be created/used.")
