"""
Middlewares package initialization
"""

from aiogram import Dispatcher

from .auth_middleware import AuthMiddleware
from .channel_middleware import ChannelSubscriptionMiddleware
from .admin_middleware import AdminMiddleware


def register_all_middlewares(dp: Dispatcher) -> None:
    """Barcha middlewarelarni ro'yxatga olish"""
    
    # Middleware tartibini saqlash muhim!
    
    # 1. Auth middleware - har doim birinchi
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    
    # 2. Admin middleware - admin handlerlar uchun
    dp.message.middleware(AdminMiddleware())
    dp.callback_query.middleware(AdminMiddleware())
    
    # 3. Channel subscription middleware - kino kodlari uchun
    dp.message.middleware(ChannelSubscriptionMiddleware())
    
    print("✅ Barcha middlewarelar ro'yxatga olindi")


__all__ = [
    "register_all_middlewares",
    "AuthMiddleware",
    "ChannelSubscriptionMiddleware", 
    "AdminMiddleware"
]