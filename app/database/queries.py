"""
Ma'lumotlar bazasi so'rovlari (Database Queries)
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import asyncpg

from .connection import get_db_connection
from .models import User, Movie, Channel, JoinedUserChannel, MovieView, UserChannelInfo, MovieStats

logger = logging.getLogger(__name__)


class DatabaseQueries:
    """Ma'lumotlar bazasi so'rovlari sinfi"""
    
    def __init__(self):
        self.db = get_db_connection()
    
    # ==================== USER QUERIES ====================
    
    async def create_user(self, tg_id: int, full_name: str, is_admin: bool = False) -> User:
        """Yangi foydalanuvchi yaratish"""
        query = """
        INSERT INTO users (tg_id, full_name, is_admin)
        VALUES ($1, $2, $3)
        ON CONFLICT (tg_id) 
        DO UPDATE SET 
            full_name = EXCLUDED.full_name,
            last_activity = CURRENT_TIMESTAMP
        RETURNING *
        """
        
        record = await self.db.fetchrow(query, tg_id, full_name, is_admin)
        return User.from_record(record)
    
    async def get_user_by_tg_id(self, tg_id: int) -> Optional[User]:
        """Telegram ID bo'yicha foydalanuvchini topish"""
        query = "SELECT * FROM users WHERE tg_id = $1"
        record = await self.db.fetchrow(query, tg_id)
        return User.from_record(record) if record else None
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """ID bo'yicha foydalanuvchini topish"""
        query = "SELECT * FROM users WHERE id = $1"
        record = await self.db.fetchrow(query, user_id)
        return User.from_record(record) if record else None
    
    async def update_user_activity(self, tg_id: int) -> None:
        """Foydalanuvchi faoliyatini yangilash"""
        query = """
        UPDATE users 
        SET last_activity = CURRENT_TIMESTAMP 
        WHERE tg_id = $1
        """
        await self.db.execute(query, tg_id)
    
    async def get_all_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Barcha foydalanuvchilar ro'yxati"""
        query = """
        SELECT * FROM users 
        ORDER BY created_at DESC 
        LIMIT $1 OFFSET $2
        """
        records = await self.db.fetch(query, limit, offset)
        return [User.from_record(record) for record in records]
    
    async def get_admin_users(self) -> List[User]:
        """Admin foydalanuvchilar ro'yxati"""
        query = "SELECT * FROM users WHERE is_admin = TRUE"
        records = await self.db.fetch(query)
        return [User.from_record(record) for record in records]
    
    async def set_user_admin(self, tg_id: int, is_admin: bool = True) -> bool:
        """Foydalanuvchini admin qilish/admin huquqini olish"""
        query = """
        UPDATE users 
        SET is_admin = $2 
        WHERE tg_id = $1
        """
        result = await self.db.execute(query, tg_id, is_admin)
        return "UPDATE 1" in result
    
    async def get_users_count(self) -> int:
        """Jami foydalanuvchilar soni"""
        query = "SELECT COUNT(*) FROM users"
        return await self.db.fetchval(query)
    
    # ==================== MOVIE QUERIES ====================
    
    async def create_movie(self, file_id: str, code: str, title: str, private_message_id: int, description: str = "") -> Movie:
        """Yangi kino yaratish - private channel ma'lumotlari bilan"""
        query = """
        INSERT INTO movie (file_id, code, title, description, private_message_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
        """
        record = await self.db.fetchrow(query, file_id, code, title, description, private_message_id)
        return Movie.from_record(record)
        
    async def get_movie_by_code(self, code: str) -> Optional[Movie]:
        """Kod bo'yicha kino topish"""
        query = "SELECT * FROM movie WHERE code = $1"
        record = await self.db.fetchrow(query, code)
        return Movie.from_record(record) if record else None
    
    async def get_movie_by_id(self, movie_id: int) -> Optional[Movie]:
        """ID bo'yicha kino topish"""
        query = "SELECT * FROM movie WHERE id = $1"
        record = await self.db.fetchrow(query, movie_id)
        return Movie.from_record(record) if record else None
    
    async def search_movies(self, search_term: str, limit: int = 10) -> List[Movie]:
        """Kino qidirish (nom bo'yicha)"""
        query = """
        SELECT * FROM movie 
        WHERE title ILIKE $1 
        ORDER BY view_count DESC 
        LIMIT $2
        """
        records = await self.db.fetch(query, f"%{search_term}%", limit)
        return [Movie.from_record(record) for record in records]
    
    async def get_popular_movies(self, limit: int = 10) -> List[Movie]:
        """Mashhur kinolar ro'yxati"""
        query = """
        SELECT * FROM movie 
        ORDER BY view_count DESC 
        LIMIT $1
        """
        records = await self.db.fetch(query, limit)
        return [Movie.from_record(record) for record in records]
    
    async def get_recent_movies(self, limit: int = 10) -> List[Movie]:
        """Yangi qo'shilgan kinolar"""
        query = """
        SELECT * FROM movie 
        ORDER BY created_at DESC 
        LIMIT $1
        """
        records = await self.db.fetch(query, limit)
        return [Movie.from_record(record) for record in records]
    
    async def update_movie(self, movie_id: int, **kwargs) -> bool:
        """Kino ma'lumotlarini yangilash"""
        if not kwargs:
            return False
        
        # Dinamik UPDATE query yaratish
        set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(kwargs.keys())])
        query = f"UPDATE movie SET {set_clause} WHERE id = $1"
        
        values = [movie_id] + list(kwargs.values())
        result = await self.db.execute(query, *values)
        return "UPDATE 1" in result
    
    async def delete_movie(self, movie_id: int) -> bool:
        """Kinoni o'chirish"""
        query = "DELETE FROM movie WHERE id = $1"
        result = await self.db.execute(query, movie_id)
        return "DELETE 1" in result
    
    async def increment_movie_views(self, movie_id: int) -> None:
        """Kino ko'rish sonini oshirish"""
        query = """
        UPDATE movie 
        SET view_count = view_count + 1 
        WHERE id = $1
        """
        await self.db.execute(query, movie_id)
    
    async def get_movies_count(self) -> int:
        """Jami kinolar soni"""
        query = "SELECT COUNT(*) FROM movie"
        return await self.db.fetchval(query)
    
    # ==================== CHANNEL QUERIES ====================
    
    async def create_channel(self, title: str, channel_link: str, channel_username: str = "", 
                            channel_id: Optional[int] = None, status: str = "aktiv") -> Channel:
        """Yangi kanal yaratish"""
        query = """
        INSERT INTO channel (channel_id, title, channel_link, channel_username, status)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
        """
        record = await self.db.fetchrow(query, channel_id, title, channel_link, channel_username, status)
        return Channel.from_record(record)
    
    async def get_all_channels(self) -> List[Channel]:
        """Barcha kanallar ro'yxati"""
        query = "SELECT * FROM channel ORDER BY created_at DESC"
        records = await self.db.fetch(query)
        return [Channel.from_record(record) for record in records]
    
    async def get_active_channels(self) -> List[Channel]:
        """Faol kanallar ro'yxati"""
        query = "SELECT * FROM channel WHERE status = 'aktiv' ORDER BY created_at DESC"
        records = await self.db.fetch(query)
        return [Channel.from_record(record) for record in records]
    
    async def get_channel_by_id(self, id: int) -> Optional[Channel]:
        """ID bo'yicha kanal topish"""
        query = "SELECT * FROM channel WHERE id = $1"
        record = await self.db.fetchrow(query, id)
        return Channel.from_record(record) if record else None
    
    async def get_channel_by_channel_id(self, channel_id: int) -> Optional[Channel]:
        """ID bo'yicha kanal topish"""
        query = "SELECT * FROM channel WHERE channel_id = $1"
        record = await self.db.fetchrow(query, channel_id)
        return Channel.from_record(record) if record else None
    
    async def get_channels_by_ids(self, channel_ids: List[int]) -> List[Channel]:
        """Bir nechta channel ID bo'yicha kanallarni olish"""
        query = """
        SELECT * FROM channel 
        WHERE channel_id = ANY($1) AND status = 'aktiv'
        ORDER BY created_at DESC
        """
        records = await self.db.fetch(query, channel_ids)
        return [Channel.from_record(record) for record in records]
    
    async def update_channel_status(self, channel_id: int, status: str) -> bool:
        """Kanal holatini yangilash"""
        query = """
        UPDATE channel 
        SET status = $2 
        WHERE id = $1
        """
        result = await self.db.execute(query, channel_id, status)
        return "UPDATE 1" in result
    
    async def delete_channel(self, channel_id: int) -> bool:
        """Kanalni o'chirish"""
        query = "DELETE FROM channel WHERE id = $1"
        result = await self.db.execute(query, channel_id)
        return "DELETE 1" in result
    
    # ==================== SUBSCRIPTION QUERIES ====================
    
    async def add_user_to_channel(self, user_id: int, channel_id: int) -> JoinedUserChannel:
        """Foydalanuvchini kanalga qo'shish"""
        query = """
        INSERT INTO joineduserannel (user_id, channel_id)
        VALUES ($1, $2)
        ON CONFLICT (user_id, channel_id) DO NOTHING
        RETURNING *
        """
        record = await self.db.fetchrow(query, user_id, channel_id)
        if record:
            return JoinedUserChannel.from_record(record)
        
        # Agar conflict bo'lsa, mavjud recordni qaytarish
        existing_query = """
        SELECT * FROM joineduserannel 
        WHERE user_id = $1 AND channel_id = $2
        """
        existing_record = await self.db.fetchrow(existing_query, user_id, channel_id)
        return JoinedUserChannel.from_record(existing_record)
    
    async def remove_user_from_channel(self, user_id: int, channel_id: int) -> bool:
        """Foydalanuvchini kanaldan chiqarish"""
        query = """
        DELETE FROM joineduserannel 
        WHERE user_id = $1 AND channel_id = $2
        """
        result = await self.db.execute(query, user_id, channel_id)
        return "DELETE 1" in result
    
    async def get_user_channels(self, user_id: int) -> List[int]:
        """Foydalanuvchi obuna bo'lgan kanallar ID lari"""
        query = """
        SELECT channel_id FROM joineduserannel 
        WHERE user_id = $1
        """
        records = await self.db.fetch(query, user_id)
        return [record['channel_id'] for record in records]
    
    async def check_user_subscription(self, user_id: int) -> UserChannelInfo:
        """Foydalanuvchi obuna holatini tekshirish"""
        # Barcha faol kanallar
        active_channels = await self.get_active_channels()
        
        # Foydalanuvchi obuna bo'lgan kanallar
        joined_channel_ids = await self.get_user_channels(user_id)
        
        # Foydalanuvchi ma'lumotlari
        user = await self.get_user_by_id(user_id)
        
        return UserChannelInfo(
            user=user,
            channels=active_channels,
            joined_channels=joined_channel_ids
        )
    
    async def get_channel_subscribers_count(self, channel_id: int) -> int:
        """Kanal obunachilari soni"""
        query = """
        SELECT COUNT(*) FROM joineduserannel 
        WHERE channel_id = $1
        """
        return await self.db.fetchval(query, channel_id)
    
    async def get_unsubscribed_users(self, channel_id: int) -> List[User]:
        """Kanalga obuna bo'lmagan foydalanuvchilar"""
        query = """
        SELECT u.* FROM users u
        WHERE u.id NOT IN (
            SELECT juc.user_id FROM joineduserannel juc 
            WHERE juc.channel_id = $1
        )
        ORDER BY u.created_at DESC
        """
        records = await self.db.fetch(query, channel_id)
        return [User.from_record(record) for record in records]
    
    # ==================== MOVIE VIEWS QUERIES ====================
    
    async def add_movie_view(self, user_id: int, movie_id: int) -> MovieView:
        """Kino ko'rishni qayd etish"""
        query = """
        INSERT INTO movie_views (user_id, movie_id)
        VALUES ($1, $2)
        RETURNING *
        """
        record = await self.db.fetchrow(query, user_id, movie_id)
        
        # Ko'rish sonini ham oshirish
        await self.increment_movie_views(movie_id)
        
        return MovieView.from_record(record)
    
    async def get_user_movie_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Foydalanuvchi kino ko'rish tarixi"""
        query = """
        SELECT mv.*, m.title, m.code, m.description
        FROM movie_views mv
        JOIN movie m ON mv.movie_id = m.id
        WHERE mv.user_id = $1
        ORDER BY mv.viewed_at DESC
        LIMIT $2
        """
        records = await self.db.fetch(query, user_id, limit)
        return [dict(record) for record in records]
    
    async def get_movie_viewers(self, movie_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Kino ko'rgan foydalanuvchilar"""
        query = """
        SELECT mv.*, u.tg_id, u.full_name
        FROM movie_views mv
        JOIN users u ON mv.user_id = u.id
        WHERE mv.movie_id = $1
        ORDER BY mv.viewed_at DESC
        LIMIT $2
        """
        records = await self.db.fetch(query, movie_id, limit)
        return [dict(record) for record in records]
    
    async def get_movie_stats(self, movie_id: int) -> Optional[MovieStats]:
        """Kino statistikasini olish"""
        # Asosiy kino ma'lumotlari
        movie = await self.get_movie_by_id(movie_id)
        if not movie:
            return None
        
        # Statistika so'rovlari
        stats_query = """
        SELECT 
            COUNT(*) as total_views,
            COUNT(DISTINCT user_id) as unique_viewers,
            COUNT(CASE WHEN viewed_at > NOW() - INTERVAL '24 hours' THEN 1 END) as recent_views
        FROM movie_views 
        WHERE movie_id = $1
        """
        
        stats_record = await self.db.fetchrow(stats_query, movie_id)
        
        return MovieStats(
            movie=movie,
            total_views=stats_record['total_views'],
            unique_viewers=stats_record['unique_viewers'],
            recent_views=stats_record['recent_views']
        )
    
    async def get_user_watched_movies_count(self, user_id: int) -> int:
        """Foydalanuvchi ko'rgan kinolar soni"""
        query = """
        SELECT COUNT(DISTINCT movie_id) 
        FROM movie_views 
        WHERE user_id = $1
        """
        return await self.db.fetchval(query, user_id)
    
    async def has_user_watched_movie(self, user_id: int, movie_id: int) -> bool:
        """Foydalanuvchi kinoni ko'rgan yoki yo'qligini tekshirish"""
        query = """
        SELECT EXISTS(
            SELECT 1 FROM movie_views 
            WHERE user_id = $1 AND movie_id = $2
        )
        """
        return await self.db.fetchval(query, user_id, movie_id)
    
    # ==================== ANALYTICS QUERIES ====================
    
    async def get_platform_statistics(self) -> Dict[str, Any]:
        """Platforma statistikasi"""
        stats_query = """
        SELECT 
            (SELECT COUNT(*) FROM users) as total_users,
            (SELECT COUNT(*) FROM users WHERE is_admin = TRUE) as admin_count,
            (SELECT COUNT(*) FROM movie) as total_movies,
            (SELECT COUNT(*) FROM channel WHERE status = 'aktiv') as active_channels,
            (SELECT COUNT(*) FROM movie_views) as total_views,
            (SELECT COUNT(*) FROM users WHERE last_activity > NOW() - INTERVAL '24 hours') as active_users_24h,
            (SELECT COUNT(*) FROM users WHERE created_at > NOW() - INTERVAL '7 days') as new_users_week
        """
        
        result = await self.db.fetchrow(stats_query)
        return dict(result)
    
    async def get_top_movies(self, limit: int = 10, days: int = 30) -> List[Dict[str, Any]]:
        """Top kinolar (ma'lum vaqt oralig'ida)"""
        query = """
        SELECT 
            m.*,
            COUNT(mv.id) as views_count,
            COUNT(DISTINCT mv.user_id) as unique_viewers
        FROM movie m
        LEFT JOIN movie_views mv ON m.id = mv.movie_id 
            AND mv.viewed_at > NOW() - INTERVAL '%s days'
        GROUP BY m.id
        ORDER BY views_count DESC, unique_viewers DESC
        LIMIT $1
        """ % days
        
        records = await self.db.fetch(query, limit)
        return [dict(record) for record in records]
    
    async def get_active_users(self, days: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """Faol foydalanuvchilar"""
        query = """
        SELECT 
            u.*,
            COUNT(mv.id) as movies_watched,
            MAX(mv.viewed_at) as last_movie_watch
        FROM users u
        LEFT JOIN movie_views mv ON u.id = mv.user_id 
            AND mv.viewed_at > NOW() - INTERVAL '%s days'
        WHERE u.last_activity > NOW() - INTERVAL '%s days'
        GROUP BY u.id
        ORDER BY movies_watched DESC, last_movie_watch DESC
        LIMIT $1
        """ % (days, days)
        
        records = await self.db.fetch(query, limit)
        return [dict(record) for record in records]
    
    async def get_daily_statistics(self, days: int = 7) -> List[Dict[str, Any]]:
        """Kunlik statistika"""
        query = """
        SELECT 
            DATE(viewed_at) as date,
            COUNT(*) as total_views,
            COUNT(DISTINCT user_id) as unique_users,
            COUNT(DISTINCT movie_id) as unique_movies
        FROM movie_views 
        WHERE viewed_at > NOW() - INTERVAL '%s days'
        GROUP BY DATE(viewed_at)
        ORDER BY date DESC
        """ % days
        
        records = await self.db.fetch(query)
        return [dict(record) for record in records]
    
    # ==================== ADMIN QUERIES ====================
    
    async def get_admin_dashboard_data(self) -> Dict[str, Any]:
        """Admin dashboard uchun ma'lumotlar"""
        # Platform statistikasi
        platform_stats = await self.get_platform_statistics()
        
        # Top kinolar (oxirgi 7 kun)
        top_movies = await self.get_top_movies(limit=5, days=7)
        
        # Faol foydalanuvchilar
        active_users = await self.get_active_users(days=1, limit=10)
        
        # Kunlik statistika
        daily_stats = await self.get_daily_statistics(days=7)
        
        return {
            'platform_stats': platform_stats,
            'top_movies': top_movies,
            'active_users': active_users,
            'daily_stats': daily_stats
        }
    
    async def search_users(self, search_term: str, limit: int = 20) -> List[User]:
        """Foydalanuvchilarni qidirish"""
        query = """
        SELECT * FROM users 
        WHERE full_name ILIKE $1 OR tg_id::text LIKE $1
        ORDER BY last_activity DESC
        LIMIT $2
        """
        records = await self.db.fetch(query, f"%{search_term}%", limit)
        return [User.from_record(record) for record in records]
    
    async def bulk_add_users_to_channel(self, user_ids: List[int], channel_id: int) -> int:
        """Ko'p foydalanuvchini kanalga qo'shish"""
        if not user_ids:
            return 0
        
        # Bulk insert uchun ma'lumotlar tayyorlash
        values = [(user_id, channel_id) for user_id in user_ids]
        
        query = """
        INSERT INTO joineduserannel (user_id, channel_id)
        VALUES ($1, $2)
        ON CONFLICT (user_id, channel_id) DO NOTHING
        """
        
        await self.db.executemany(query, values)
        
        # Qo'shilgan foydalanuvchilar sonini qaytarish
        count_query = """
        SELECT COUNT(*) FROM joineduserannel 
        WHERE user_id = ANY($1) AND channel_id = $2
        """
        return await self.db.fetchval(count_query, user_ids, channel_id)
    
    async def cleanup_old_views(self, days: int = 90) -> int:
        """Eski ko'rishlarni tozalash"""
        query = """
        DELETE FROM movie_views 
        WHERE viewed_at < NOW() - INTERVAL '%s days'
        """ % days
        
        result = await self.db.execute(query)
        # "DELETE X" formatidan sonni ajratib olish
        return int(result.split()[-1]) if result.startswith("DELETE") else 0
    
    # ==================== BACKUP & MAINTENANCE ====================
    
    async def backup_data(self) -> Dict[str, Any]:
        """Ma'lumotlarni backup qilish (JSON format)"""
        backup_data = {}
        
        # Users
        users = await self.get_all_users(limit=10000)
        backup_data['users'] = [user.to_dict() for user in users]
        
        # Movies
        movies_query = "SELECT * FROM movie ORDER BY id"
        movies_records = await self.db.fetch(movies_query)
        backup_data['movies'] = [dict(record) for record in movies_records]
        
        # Channels
        channels = await self.get_all_channels()
        backup_data['channels'] = [channel.to_dict() for channel in channels]
        
        # Subscriptions
        subs_query = "SELECT * FROM joineduserannel ORDER BY id"
        subs_records = await self.db.fetch(subs_query)
        backup_data['subscriptions'] = [dict(record) for record in subs_records]
        
        backup_data['backup_date'] = datetime.now().isoformat()
        backup_data['total_records'] = sum(len(v) for k, v in backup_data.items() if isinstance(v, list))
        
        return backup_data
    
    async def get_database_size(self) -> Dict[str, int]:
        """Ma'lumotlar bazasi hajmini olish"""
        size_query = """
        SELECT 
            schemaname,
            tablename,
            attname,
            n_distinct,
            correlation
        FROM pg_stats 
        WHERE schemaname = 'public'
        """
        
        # Har bir jadval uchun qatorlar soni
        tables = ['users', 'movie', 'channel', 'joineduserannel', 'movie_views']
        sizes = {}
        
        for table in tables:
            count_query = f"SELECT COUNT(*) FROM {table}"
            sizes[table] = await self.db.fetchval(count_query)
        
        return sizes