"""
Handlers package initialization
"""

from aiogram import Dispatcher

from .start import register_start_handlers
from .user_handlers import register_user_handlers
from .admin_handlers import register_admin_handlers
from .movie_handlers import register_movie_handlers
from .channel_handlers import register_channel_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    """Barcha handlerlarni ro'yxatga olish"""
    
    # Handlerlar tartibini saqlash muhim!
    # Admin handlerlar birinchi bo'lishi kerak
    register_admin_handlers(dp)
    
    # Keyin start va asosiy handlerlar
    register_start_handlers(dp)
    
    # Kanal tekshirish handlerlari
    register_channel_handlers(dp)
    
    # Kino handlerlari
    register_movie_handlers(dp)
    
    # Oxirida user handlerlar
    register_user_handlers(dp)
    
    print("✅ Barcha handlerlar ro'yxatga olindi")


__all__ = [
    "register_all_handlers",
    "register_admin_handlers",
    "register_start_handlers",
    "register_user_handlers", 
    "register_movie_handlers",
    "register_channel_handlers"
]