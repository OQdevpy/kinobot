"""
Kanal obuna filtri
"""

from typing import Any, Dict
from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.database import DatabaseQueries


class ChannelSubscriptionFilter(BaseFilter):
    """Kanal obuna filtri - faqat obuna bo'lgan foydalanuvchilar o'tadi"""
    
    async def __call__(self, message: Message, **kwargs) -> bool | Dict[str, Any]:
        """Obuna holatini tekshirish"""
        
        if not message.from_user or message.from_user.is_bot:
            return False
        
        try:
            db_queries = DatabaseQueries()
            
            # Foydalanuvchini topish
            user = await db_queries.get_user_by_tg_id(message.from_user.id)
            
            if not user:
                return False
            
            # Obuna holatini tekshirish
            subscription_info = await db_queries.check_user_subscription(user.id)
            
            # Barcha kanallarga obuna bo'lgan yoki yo'q
            is_subscribed_to_all = subscription_info.is_subscribed_to_all()
            
            if is_subscribed_to_all:
                return {
                    'user_db': user,
                    'subscription_info': subscription_info
                }
            
            return False
        
        except Exception as e:
            print(f"Channel subscription filter error: {e}")
            return False


class NotSubscribedFilter(BaseFilter):
    """Obuna bo'lmagan foydalanuvchilar filtri"""
    
    async def __call__(self, message: Message, **kwargs) -> bool | Dict[str, Any]:
        """Obuna bo'lmaganlarni tekshirish"""
        
        if not message.from_user or message.from_user.is_bot:
            return False
        
        try:
            db_queries = DatabaseQueries()
            
            # Foydalanuvchini topish
            user = await db_queries.get_user_by_tg_id(message.from_user.id)
            
            if not user:
                return False
            
            # Obuna holatini tekshirish
            subscription_info = await db_queries.check_user_subscription(user.id)
            
            # Obuna bo'lmagan kanalllar bor yoki yo'q
            unsubscribed_channels = subscription_info.get_unjoined_channels()
            
            if unsubscribed_channels:
                return {
                    'user_db': user,
                    'subscription_info': subscription_info,
                    'unsubscribed_channels': unsubscribed_channels
                }
            
            return False
        
        except Exception as e:
            print(f"Not subscribed filter error: {e}")
            return False


class HasActiveChannelsFilter(BaseFilter):
    """Faol kanallar mavjudligini tekshirish filtri"""
    
    async def __call__(self, message: Message, **kwargs) -> bool | Dict[str, Any]:
        """Faol kanallar borligini tekshirish"""
        
        try:
            db_queries = DatabaseQueries()
            
            # Faol kanallarni olish
            active_channels = await db_queries.get_active_channels()
            
            if active_channels:
                return {
                    'active_channels': active_channels,
                    'channels_count': len(active_channels)
                }
            
            return False
        
        except Exception as e:
            print(f"Has active channels filter error: {e}")
            return False