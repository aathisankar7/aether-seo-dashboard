import os
import asyncio
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    """
    Manages asynchronous connections to MySQL and PostgreSQL databases.
    Inspired by the existing MongoDB manager architecture.
    """
    def __init__(self):
        self.mysql_url = os.getenv("MYSQL_URL")
        self.postgres_url = os.getenv("POSTGRES_URL")
        
        # Engines and Session Makers
        self._mysql_engine = None
        self._postgres_engine = None
        self._mysql_session_factory = None
        self._postgres_session_factory = None

    async def initialize(self):
        """Initialize database engines."""
        if self.mysql_url:
            self._mysql_engine = create_async_engine(self.mysql_url, echo=False)
            self._mysql_session_factory = async_sessionmaker(
                self._mysql_engine, expire_on_commit=False, class_=AsyncSession
            )
        
        if self.postgres_url:
            self._postgres_engine = create_async_engine(self.postgres_url, echo=False)
            self._postgres_session_factory = async_sessionmaker(
                self._postgres_engine, expire_on_commit=False, class_=AsyncSession
            )

    async def get_mysql_session(self) -> Optional[AsyncSession]:
        """Get an async session for MySQL."""
        if not self._mysql_session_factory:
            await self.initialize()
        return self._mysql_session_factory() if self._mysql_session_factory else None

    async def get_postgres_session(self) -> Optional[AsyncSession]:
        """Get an async session for PostgreSQL."""
        if not self._postgres_session_factory:
            await self.initialize()
        return self._postgres_session_factory() if self._postgres_session_factory else None

    async def test_connections(self):
        """Verify connectivity to both databases."""
        results = {"mysql": "Not Configured", "postgres": "Not Configured"}
        
        if self.mysql_url:
            try:
                async with self._mysql_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    results["mysql"] = "Connected Successfully"
            except Exception as e:
                results["mysql"] = f"Connection Failed: {str(e)}"
        
        if self.postgres_url:
            try:
                async with self._postgres_engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    results["postgres"] = "Connected Successfully"
            except Exception as e:
                results["postgres"] = f"Connection Failed: {str(e)}"
        
        return results

    async def close(self):
        """Dispose of the engines."""
        if self._mysql_engine:
            await self._mysql_engine.dispose()
        if self._postgres_engine:
            await self._postgres_engine.dispose()

# Global Instance
db_manager = DatabaseManager()
