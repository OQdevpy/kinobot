"""
Admin tekshirish middleware
"""

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.database import DatabaseQueries
from app.config import settings


class AdminMiddleware(BaseMiddleware):
    """Admin huquqlarini tekshirish middleware"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        user = None
        
        # Event turini aniqlash
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        
        if user and not user.is_bot:
            admin_status = await self._check_admin_status(user.id)
            
            # Admin ma'lumotlarini data ga qo'shish
            data['is_admin'] = admin_status['is_admin']
            data['is_super_admin'] = admin_status['is_super_admin']
            data['admin_level'] = admin_status['admin_level']
        else:
            # Bot yoki noma'lum foydalanuvchi
            data['is_admin'] = False
            data['is_super_admin'] = False
            data['admin_level'] = 0
        
        return await handler(event, data)
    
    async def _check_admin_status(self, user_tg_id: int) -> Dict[str, Any]:
        """Admin holatini tekshirish"""
        
        db_queries = DatabaseQueries()
        
        try:
            # Ma'lumotlar bazasidan tekshirish
            user = await db_queries.get_user_by_tg_id(user_tg_id)
            
            is_admin = False
            is_super_admin = False
            admin_level = 0
            
            if user and user.is_admin:
                is_admin = True
                admin_level = 1
            
            # Super admin tekshirish (config dan)
            if user_tg_id in settings.admin_ids:
                is_super_admin = True
                is_admin = True
                admin_level = 2
                
                # Agar ma'lumotlar bazasida admin emas bo'lsa, admin qilish
                if user and not user.is_admin:
                    await db_queries.set_user_admin(user_tg_id, True)
            
            return {
                'is_admin': is_admin,
                'is_super_admin': is_super_admin,
                'admin_level': admin_level
            }
        
        except Exception as e:
            print(f"Admin middleware error: {e}")
            return {
                'is_admin': False,
                'is_super_admin': False,
                'admin_level': 0
            }