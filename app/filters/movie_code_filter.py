"""
Kino kod filtri
"""

import re
from typing import Any, Dict
from aiogram.filters import BaseFilter
from aiogram.types import Message

from app.database import DatabaseQueries


class MovieCodeFilter(BaseFilter):
    """Kino kodi filtri"""
    
    def __init__(self, check_exists: bool = False):
        self.check_exists = check_exists
        # Kino kodi pattern: 3-20 ta harf, raqam va _ belgisi
        self.pattern = re.compile(r'^[A-Z0-9_]{3,20}$')
    
    async def __call__(self, message: Message, **kwargs) -> bool | Dict[str, Any]:
        """Kino kodini tekshirish"""
        
        if not message.text:
            return False
        
        text = message.text.strip().upper()
        
        # Pattern bo'yicha tekshirish
        if not self.pattern.match(text):
            return False
        
        # Agar mavjudligini tekshirish talab qilinmasa
        if not self.check_exists:
            return {'movie_code': text}
        
        # Ma'lumotlar bazasida mavjudligini tekshirish
        try:
            db_queries = DatabaseQueries()
            movie = await db_queries.get_movie_by_code(text)
            
            if movie:
                return {
                    'movie_code': text,
                    'movie': movie
                }
            
            return False
        
        except Exception as e:
            print(f"Movie code filter error: {e}")
            return False


class ExistingMovieCodeFilter(MovieCodeFilter):
    """Mavjud kino kodi filtri"""
    
    def __init__(self):
        super().__init__(check_exists=True)


class ValidMovieCodeFormatFilter(BaseFilter):
    """To'g'ri kino kod formati filtri"""
    
    def __init__(self):
        self.pattern = re.compile(r'^[A-Z0-9_]{3,20}$')
    
    async def __call__(self, message: Message, **kwargs) -> bool | Dict[str, Any]:
        """Format tekshirish"""
        
        if not message.text:
            return False
        
        text = message.text.strip().upper()
        
        if self.pattern.match(text):
            return {'formatted_code': text}
        
        return False


class PossibleMovieCodeFilter(BaseFilter):
    """Mumkin bo'lgan kino kodi filtri (keng qamrovli)"""
    
    def __init__(self):
        # Keng qamrovli pattern
        self.pattern = re.compile(r'^[A-Z0-9_-]{2,25}$')
    
    async def __call__(self, message: Message, **kwargs) -> bool | Dict[str, Any]:
        """Mumkin bo'lgan kod tekshirish"""
        
        if not message.text:
            return False
        
        text = message.text.strip().upper()
        
        # Asosiy komandalar yoki uzun matnlarni istisno qilish
        if text.startswith('/') or len(text.split()) > 1:
            return False
        
        if self.pattern.match(text):
            return {'possible_code': text}
        
        return False