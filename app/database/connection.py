"""
PostgreSQL ulanish va connection pool boshqaruvi
"""

import asyncio
import asyncpg
from typing import Optional, Dict, Any
import logging
from contextlib import asynccontextmanager

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """PostgreSQL ma'lumotlar bazasi ulanish sinfi"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self._is_connected = False
    
    async def connect(self) -> None:
        """Ma'lumotlar bazasiga ulanish va connection pool yaratish"""
        try:
            self.pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=1,
                max_size=10,
                command_timeout=60,
                server_settings={
                    'jit': 'off'  # Performance uchun
                }
            )
            self._is_connected = True
            logger.info("✅ PostgreSQL connection pool yaratildi")
            
        except Exception as e:
            logger.error(f"❌ Ma'lumotlar bazasiga ulanishda xatolik: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Ma'lumotlar bazasi ulanishini yopish"""
        if self.pool:
            await self.pool.close()
            self._is_connected = False
            logger.info("✅ PostgreSQL connection pool yopildi")
    
    @property
    def is_connected(self) -> bool:
        """Ulanish holatini tekshirish"""
        return self._is_connected and self.pool is not None
    
    @asynccontextmanager
    async def get_connection(self):
        """Connection context manager"""
        if not self.is_connected:
            raise RuntimeError("Ma'lumotlar bazasi ulanmagan!")
        
        async with self.pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"Database operation error: {e}")
                raise
    
    async def execute(self, query: str, *args) -> str:
        """SQL so'rovni bajarish (INSERT, UPDATE, DELETE)"""
        async with self.get_connection() as conn:
            try:
                result = await conn.execute(query, *args)
                logger.debug(f"Query executed: {query[:100]}...")
                return result
            except Exception as e:
                logger.error(f"Execute error: {e}")
                raise
    
    async def fetch(self, query: str, *args) -> list:
        """SQL so'rovdan ko'p natija olish (SELECT)"""
        async with self.get_connection() as conn:
            try:
                result = await conn.fetch(query, *args)
                logger.debug(f"Fetch query: {query[:100]}... | Results: {len(result)}")
                return result
            except Exception as e:
                logger.error(f"Fetch error: {e}")
                raise
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """SQL so'rovdan bitta natija olish"""
        async with self.get_connection() as conn:
            try:
                result = await conn.fetchrow(query, *args)
                logger.debug(f"Fetchrow query: {query[:100]}...")
                return result
            except Exception as e:
                logger.error(f"Fetchrow error: {e}")
                raise
    
    async def fetchval(self, query: str, *args):
        """SQL so'rovdan bitta qiymat olish"""
        async with self.get_connection() as conn:
            try:
                result = await conn.fetchval(query, *args)
                logger.debug(f"Fetchval query: {query[:100]}...")
                return result
            except Exception as e:
                logger.error(f"Fetchval error: {e}")
                raise
    
    async def executemany(self, query: str, args_list: list) -> None:
        """Ko'p so'rovlarni bir vaqtda bajarish"""
        async with self.get_connection() as conn:
            try:
                await conn.executemany(query, args_list)
                logger.debug(f"Executemany: {len(args_list)} queries")
            except Exception as e:
                logger.error(f"Executemany error: {e}")
                raise
    
    async def transaction(self):
        """Transaction context manager"""
        if not self.is_connected:
            raise RuntimeError("Ma'lumotlar bazasi ulanmagan!")
        
        return self.pool.acquire()
    
    async def health_check(self) -> bool:
        """Ma'lumotlar bazasi holatini tekshirish"""
        try:
            result = await self.fetchval("SELECT 1")
            return result == 1
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global database connection instance
db = DatabaseConnection()


async def init_db() -> None:
    """Ma'lumotlar bazasini ishga tushirish"""
    await db.connect()
    
    # Health check
    if await db.health_check():
        logger.info("✅ Ma'lumotlar bazasi tayyor")
    else:
        logger.error("❌ Ma'lumotlar bazasi health check muvaffaqiyatsiz")
        raise RuntimeError("Database health check failed")


async def close_db() -> None:
    """Ma'lumotlar bazasini yopish"""
    await db.disconnect()


def get_db_connection() -> DatabaseConnection:
    """Database connection instance olish"""
    return db


# Transaction decorator
def db_transaction(func):
    """Database transaction decorator"""
    async def wrapper(*args, **kwargs):
        async with db.transaction() as conn:
            try:
                # Connection ni function ga uzatish
                if 'connection' in kwargs:
                    kwargs['connection'] = conn
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f"Transaction error in {func.__name__}: {e}")
                raise
    return wrapper


# Connection pool statistikasi
async def get_pool_stats() -> Dict[str, Any]:
    """Connection pool statistikasini olish"""
    if not db.pool:
        return {"status": "disconnected"}
    
    return {
        "status": "connected",
        "size": db.pool.get_size(),
        "idle_connections": db.pool.get_idle_size(),
        "max_size": db.pool.get_max_size(),
        "min_size": db.pool.get_min_size()
    }