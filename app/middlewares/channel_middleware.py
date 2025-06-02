"""
Kanal obuna middleware
"""

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
import re

from app.database import DatabaseQueries


class ChannelSubscriptionMiddleware(BaseMiddleware):
    """Kanal obuna tekshirish middleware"""
    
    def __init__(self):
        # Kino kodi regex pattern
        self.movie_code_pattern = re.compile(r'^[A-Z0-9_]{3,20}$')
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        # Faqat message lar uchun ishlaydi
        if not isinstance(event, Message):
            return await handler(event, data)
        
        # Faqat text message lar uchun
        if not event.text:
            return await handler(event, data)
        
        # Kino kodi ekanligini tekshirish
        text = event.text.strip().upper()
        
        if not self.movie_code_pattern.match(text):
            return await handler(event, data)
        
        # Foydalanuvchi obuna holatini tekshirish
        subscription_status = await self._check_user_subscription(event.from_user.id)
        
        # Subscription ma'lumotlarini data ga qo'shish
        data['is_subscribed_to_all'] = subscription_status['is_subscribed']
        data['unsubscribed_channels'] = subscription_status['unsubscribed_channels']
        data['subscription_info'] = subscription_status['subscription_info']
        
        return await handler(event, data)
    
    async def _check_user_subscription(self, user_tg_id: int) -> Dict[str, Any]:
        """Foydalanuvchi obuna holatini tekshirish"""
        
        db_queries = DatabaseQueries()
        
        try:
            # Foydalanuvchini topish
            user = await db_queries.get_user_by_tg_id(user_tg_id)
            
            if not user:
                return {
                    'is_subscribed': False,
                    'unsubscribed_channels': [],
                    'subscription_info': None
                }
            
            # Obuna holatini tekshirish
            subscription_info = await db_queries.check_user_subscription(user.id)
            
            # Obuna bo'lmagan kanallar
            unsubscribed_channels = subscription_info.get_unjoined_channels()
            
            return {
                'is_subscribed': len(unsubscribed_channels) == 0,
                'unsubscribed_channels': unsubscribed_channels,
                'subscription_info': subscription_info
            }
        
        except Exception as e:
            print(f"Channel subscription middleware error: {e}")
            return {
                'is_subscribed': False,
                'unsubscribed_channels': [],
                'subscription_info': None
            }