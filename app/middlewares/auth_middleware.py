"""
Autentifikatsiya middleware
"""

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.database import DatabaseQueries


class AuthMiddleware(BaseMiddleware):
    """Foydalanuvchi autentifikatsiya va faoliyat tracking middleware"""
    
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
            await self._process_user(user)
            
            # User ma'lumotlarini data ga qo'shish
            data['user_id'] = user.id
            data['user_full_name'] = user.full_name
            data['user_username'] = user.username
        
        return await handler(event, data)
    
    async def _process_user(self, user) -> None:
        """Foydalanuvchini qayta ishlash"""
        db_queries = DatabaseQueries()
        
        try:
            # Foydalanuvchi mavjudligini tekshirish
            existing_user = await db_queries.get_user_by_tg_id(user.id)
            
            if existing_user:
                # Mavjud foydalanuvchi faoliyatini yangilash
                await db_queries.update_user_activity(user.id)
                
                # Ism o'zgargan bo'lsa yangilash
                if existing_user.full_name != (user.full_name or "Noma'lum"):
                    await db_queries.create_user(
                        tg_id=user.id,
                        full_name=user.full_name or "Noma'lum",
                        is_admin=existing_user.is_admin
                    )
            else:
                # Yangi foydalanuvchi yaratish
                await db_queries.create_user(
                    tg_id=user.id,
                    full_name=user.full_name or "Noma'lum",
                    is_admin=False
                )
                
                print(f"New user registered: {user.id} - {user.full_name}")
        
        except Exception as e:
            print(f"Auth middleware error: {e}")
            # Xatolik bo'lsa ham handler ishlab ketsin