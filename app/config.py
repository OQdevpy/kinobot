"""
Konfiguratsiya sozlamalari - Channel ID lar bilan
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Bot konfiguratsiya sozlamalari"""
    
    bot_token: str
    database_url: str
    admin_ids: List[int] = []
    debug: bool = False
    log_level: str = "INFO"
    
    # Channel ID lar - .env dagi nomi bilan mos kelishi kerak
    publish_channel_id: int = 0  # PUBLISH_CHANNEL_ID
    private_channel_id: int = 0  # PRIVATE_CHANNEL_ID (PRiVATE_CHANNEL_ID emas!)
    publish_channel_link: str = "https://t.me/your_publish_channel"  # Publish channel link
    private_channel_link: str = "https://t.me/your_private_channel"  # Private channel link

    bot_username: str = "your_bot_username"  # Bot username
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Qo'shimcha maydonlarga ruxsat berish
        extra = "ignore"
        # Field aliaslar
        fields = {
            'private_channel_id': {'env': ['PRIVATE_CHANNEL_ID', 'PRiVATE_CHANNEL_ID']}

        }
    
    @classmethod
    def parse_admin_ids(cls, v):
        """Admin ID larni parse qilish"""
        if isinstance(v, str):
            # String formatdan list ga o'tkazish
            if v.startswith('[') and v.endswith(']'):
                # [123,456] formatini parse qilish
                v = v[1:-1]  # [] ni olib tashlash
            
            if v:
                # Vergul bilan ajratilgan ID larni list ga aylantirish
                return [int(x.strip()) for x in v.split(',') if x.strip()]
            return []
        return v if isinstance(v, list) else []


# Settings instance yaratish
try:
    settings = Settings()
    
    # Admin IDs ni alohida parse qilish agar string bo'lsa
    admin_ids_env = os.getenv('ADMIN_IDS', '')
    if admin_ids_env:
        settings.admin_ids = Settings.parse_admin_ids(admin_ids_env)
    
    print(f"✅ Konfiguratsiya yuklandi:")
    print(f"   - Database URL: {settings.database_url}")
    print(f"   - Admin IDs: {settings.admin_ids}")
    print(f"   - Debug mode: {settings.debug}")
    print(f"   - Log level: {settings.log_level}")
    print(f"   - Publish Channel: {settings.publish_channel_id}")
    print(f"   - Private Channel: {settings.private_channel_id}")
    print(f"   - Publish Channel Link: {settings.publish_channel_link}")
    print(f"   - Private Channel Link: {settings.private_channel_link}")
    
except Exception as e:
    print(f"❌ Konfiguratsiya yuklashda xatolik: {e}")
    print("\n💡 .env faylini tekshiring:")
    print("   BOT_TOKEN=your_bot_token")
    print("   DATABASE_URL=postgresql://user:pass@localhost/db")
    print("   ADMIN_IDS=123456789,987654321")
    print("   PUBLISH_CHANNEL_ID=-1001234567890")
    print("   PRIVATE_CHANNEL_ID=-1009876543210")
    raise