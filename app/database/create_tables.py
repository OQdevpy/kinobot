"""
Ma'lumotlar bazasi jadvallarini yaratish uchun script
"""

import asyncio
import asyncpg
from typing import Optional
import sys
import os

# Root katalogni PATH ga qo'shish
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.config import settings


class DatabaseCreator:
    """Ma'lumotlar bazasi jadvallarini yaratish uchun klass"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection: Optional[asyncpg.Connection] = None
    
    async def connect(self) -> None:
        """Ma'lumotlar bazasiga ulanish"""
        try:
            self.connection = await asyncpg.connect(self.database_url)
            print("✅ Ma'lumotlar bazasiga muvaffaqiyatli ulandi")
        except Exception as e:
            print(f"❌ Ma'lumotlar bazasiga ulanishda xatolik: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Ma'lumotlar bazasi ulanishini yopish"""
        if self.connection:
            await self.connection.close()
            print("✅ Ma'lumotlar bazasi ulanishi yopildi")
    
    async def create_users_table(self) -> None:
        """Users jadvalini yaratish"""
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            tg_id BIGINT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Index qo'shish tez qidirish uchun
        CREATE INDEX IF NOT EXISTS idx_users_tg_id ON users(tg_id);
        CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin);
        """
        
        await self.connection.execute(query)
        print("✅ Users jadvali yaratildi")
    
    async def create_movie_table(self) -> None:
        """Movie jadvalini yaratish"""
        query = """
        CREATE TABLE IF NOT EXISTS movie (
            id SERIAL PRIMARY KEY,
            file_id TEXT NOT NULL,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            private_message_id INTEGER NOT NULL,  -- Private channel message ID
            view_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Index qo'shish
        CREATE INDEX IF NOT EXISTS idx_movie_code ON movie(code);
        CREATE INDEX IF NOT EXISTS idx_movie_title ON movie(title);
        CREATE INDEX IF NOT EXISTS idx_movie_view_count ON movie(view_count DESC);
        """
        
        await self.connection.execute(query)
        print("✅ Movie jadvali yaratildi")
    
    async def create_channel_table(self) -> None:
        """Channel jadvalini yaratish"""
        query = """
        CREATE TABLE IF NOT EXISTS channel (
            id SERIAL PRIMARY KEY,
            channel_id BIGINT UNIQUE,  -- Telegram kanal ID (-100 bilan boshlanuvchi)
            title TEXT NOT NULL,
            channel_link TEXT NOT NULL,
            channel_username TEXT,
            status TEXT DEFAULT 'aktiv' CHECK (status IN ('aktiv', 'noaktiv')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Index qo'shish
        CREATE INDEX IF NOT EXISTS idx_channel_status ON channel(status);
        CREATE INDEX IF NOT EXISTS idx_channel_username ON channel(channel_username);
        CREATE INDEX IF NOT EXISTS idx_channel_id ON channel(channel_id);
        """
        
        await self.connection.execute(query)
        print("✅ Channel jadvali yaratildi")
        
    async def create_joined_user_channel_table(self) -> None:
        """JoinedUserChannel jadvalini yaratish"""
        query = """
        CREATE TABLE IF NOT EXISTS joineduserannel (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            channel_id INTEGER REFERENCES channel(id) ON DELETE CASCADE,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, channel_id)
        );
        
        -- Index qo'shish
        CREATE INDEX IF NOT EXISTS idx_joined_user_id ON joineduserannel(user_id);
        CREATE INDEX IF NOT EXISTS idx_joined_channel_id ON joineduserannel(channel_id);
        """
        
        await self.connection.execute(query)
        print("✅ JoinedUserChannel jadvali yaratildi")
    
    async def create_movie_views_table(self) -> None:
        """MovieViews jadvalini yaratish"""
        query = """
        CREATE TABLE IF NOT EXISTS movie_views (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            movie_id INTEGER REFERENCES movie(id) ON DELETE CASCADE,
            viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Index qo'shish
        CREATE INDEX IF NOT EXISTS idx_views_user_id ON movie_views(user_id);
        CREATE INDEX IF NOT EXISTS idx_views_movie_id ON movie_views(movie_id);
        CREATE INDEX IF NOT EXISTS idx_views_date ON movie_views(viewed_at DESC);
        """
        
        await self.connection.execute(query)
        print("✅ MovieViews jadvali yaratildi")
    
    async def create_admin_users(self) -> None:
        """Admin foydalanuvchilarni yaratish"""
        if not settings.admin_ids:
            print("⚠️  Admin ID lari konfiguratsiyada topilmadi")
            return
        
        for admin_id in settings.admin_ids:
            try:
                query = """
                INSERT INTO users (tg_id, full_name, is_admin) 
                VALUES ($1, $2, TRUE)
                ON CONFLICT (tg_id) 
                DO UPDATE SET is_admin = TRUE
                """
                await self.connection.execute(query, admin_id, f"Admin {admin_id}")
                print(f"✅ Admin {admin_id} yaratildi/yangilandi")
            except Exception as e:
                print(f"❌ Admin {admin_id} yaratishda xatolik: {e}")
    
    async def create_sample_data(self) -> None:
        """Namuna ma'lumotlar qo'shish (ixtiyoriy)"""
        try:
            # Namuna kanal qo'shish
            channel_query = """
            INSERT INTO channel (channel_id, title, channel_link, channel_username, status)
            VALUES 
                (-1002674232945,'Kino yopiq', 'https://t.me/+a8WwoLUCv_05Njdi', '@kinoyopiq', 'aktiv'),
                (-1002552876822, 'Kino ochiq', 'https://t.me/kinoochiq', '@kinoochiq', 'aktiv')
            ON CONFLICT DO NOTHING
            """
            await self.connection.execute(channel_query)
            print("✅ Namuna kanallar qo'shildi")
            
            # Namuna kino qo'shish
            movie_query = """
            INSERT INTO movie (file_id, code, title, description, private_message_id)
            VALUES 
                ('sample_file_id_1', 'DEMO001', 'Demo Kino 1', 'Bu demo kino tavsifi', 123456789),
                ('sample_file_id_2', 'DEMO002', 'Demo Kino 2', 'Ikkinchi demo kino tavsifi', 987654321)
            ON CONFLICT (code) DO NOTHING
            """
            await self.connection.execute(movie_query)
            print("✅ Namuna kinolar qo'shildi")
            
        except Exception as e:
            print(f"⚠️  Namuna ma'lumotlar qo'shishda xatolik: {e}")
    
    async def create_all_tables(self) -> None:
        """Barcha jadvallarni yaratish"""
        print("🚀 Ma'lumotlar bazasi jadvallarini yaratish boshlandi...")
        
        await self.connect()
        
        try:
            await self.create_users_table()
            await self.create_movie_table()
            await self.create_channel_table()
            await self.create_joined_user_channel_table()
            await self.create_movie_views_table()
            
            print("\n📋 Admin foydalanuvchilarni yaratish...")
            await self.create_admin_users()
            
            print("\n📋 Namuna ma'lumotlar qo'shish...")
            await self.create_sample_data()
            
            print("\n🎉 Barcha jadvallar muvaffaqiyatli yaratildi!")
            
        except Exception as e:
            print(f"❌ Jadvallar yaratishda xatolik: {e}")
            raise
        finally:
            await self.disconnect()
    
    async def drop_all_tables(self) -> None:
        """Barcha jadvallarni o'chirish (ehtiyotkorlik bilan!)"""
        confirm = input("⚠️  Barcha jadvallarni o'chirishni xohlaysizmi? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Operatsiya bekor qilindi")
            return
        
        await self.connect()
        
        try:
            tables = ['movie_views', 'joineduserannel', 'channel', 'movie', 'users']
            
            for table in tables:
                await self.connection.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                print(f"✅ {table} jadvali o'chirildi")
            
            print("🗑️  Barcha jadvallar o'chirildi!")
            
        except Exception as e:
            print(f"❌ Jadvallarni o'chirishda xatolik: {e}")
            raise
        finally:
            await self.disconnect()


async def main():
    """Asosiy funksiya"""
    creator = DatabaseCreator(settings.database_url)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        await creator.drop_all_tables()
    else:
        await creator.create_all_tables()


if __name__ == "__main__":
    print("🔧 Telegram Kinematika Database Creator")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Operatsiya foydalanuvchi tomonidan to'xtatildi")
    except Exception as e:
        print(f"\n💥 Kutilmagan xatolik: {e}")
        sys.exit(1)