"""
Admin filtri
"""

from typing import Any, Dict
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from app.database import DatabaseQueries
from app.config import settings


class AdminFilter(BaseFilter):
    """Admin foydalanuvchilarini filtrlash"""
    
    def __init__(self, require_super_admin: bool = False):
        self.require_super_admin = require_super_admin
    
    async def __call__(self, event: Message | CallbackQuery, **kwargs) -> bool | Dict[str, Any]:
        """Admin tekshirish"""
        
        if not event.from_user or event.from_user.is_bot:
            return False
        
        user_tg_id = event.from_user.id
        
        # Super admin tekshirish (config dan)
        is_super_admin = user_tg_id in settings.admin_ids
        
        if self.require_super_admin:
            return is_super_admin
        
        # Oddiy admin tekshirish
        if is_super_admin:
            return True
        
        # Ma'lumotlar bazasidan tekshirish
        try:
            db_queries = DatabaseQueries()
            user = await db_queries.get_user_by_tg_id(user_tg_id)
            
            if user and user.is_admin:
                return True
            
        except Exception as e:
            print(f"Admin filter error: {e}")
        
        return False


class SuperAdminFilter(AdminFilter):
    """Super admin filtri"""
    
    def __init__(self):
        super().__init__(require_super_admin=True)


class AdminOrOwnerFilter(BaseFilter):
    """Admin yoki kanal egasi filtri"""
    
    async def __call__(self, event: Message | CallbackQuery, **kwargs) -> bool:
        """Admin yoki owner tekshirish"""
        
        if not event.from_user or event.from_user.is_bot:
            return False
        
        user_tg_id = event.from_user.id
        
        # Super admin har doim ruxsat
        if user_tg_id in settings.admin_ids:
            return True
        
        # Admin tekshirish
        admin_filter = AdminFilter()
        return await admin_filter(event, **kwargs)