"""
SQLAlchemy modellari (ma'lumotlar strukturasi)
"""

from datetime import datetime
from typing import Optional, List, Union
from dataclasses import dataclass
from enum import Enum


class ChannelStatus(str, Enum):
    """Kanal holati"""
    AKTIV = "aktiv"
    NOAKTIV = "noaktiv"


@dataclass
class User:
    """Foydalanuvchi modeli"""
    id: Optional[int] = None
    tg_id: int = 0
    full_name: str = ""
    is_admin: bool = False
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
    
    @classmethod
    def from_record(cls, record) -> 'User':
        """Database record dan User obyekti yaratish"""
        if not record:
            return None
        
        return cls(
            id=record['id'],
            tg_id=record['tg_id'],
            full_name=record['full_name'],
            is_admin=record['is_admin'],
            created_at=record['created_at'],
            last_activity=record['last_activity']
        )
    
    def to_dict(self) -> dict:
        """User obyektini dict ga aylantirish"""
        return {
            'id': self.id,
            'tg_id': self.tg_id,
            'full_name': self.full_name,
            'is_admin': self.is_admin,
            'created_at': self.created_at,
            'last_activity': self.last_activity
        }
    
    def is_new_user(self) -> bool:
        """Yangi foydalanuvchi ekanligini tekshirish"""
        return self.id is None


@dataclass
class Movie:
    """Kino modeli - Private channel ma'lumotlari bilan"""
    id: Optional[int] = None
    file_id: str = ""
    code: str = ""
    title: str = ""
    description: str = ""
    private_message_id: int = 0  # Private channeldagi message ID
    view_count: int = 0
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @classmethod
    def from_record(cls, record) -> 'Movie':
        """Database record dan Movie obyekti yaratish"""
        if not record:
            return None
        
        return cls(
            id=record['id'],
            file_id=record['file_id'],
            code=record['code'],
            title=record['title'],
            description=record.get('description', ''),
            private_message_id=record.get('private_message_id'),
            view_count=record.get('view_count', 0),
            created_at=record['created_at']
        )
    
    def to_dict(self) -> dict:
        """Movie obyektini dict ga aylantirish"""
        return {
            'id': self.id,
            'file_id': self.file_id,
            'code': self.code,
            'title': self.title,
            'description': self.description,
            'private_message_id': self.private_message_id,
            'view_count': self.view_count,
            'created_at': self.created_at
        }
    
    def increment_view_count(self):
        """Ko'rish sonini oshirish"""
        self.view_count += 1
    
    def get_watch_link(self, bot_username: str) -> str:
        """Kino tomosha qilish uchun bot link yaratish"""
        return f"https://t.me/{bot_username}?start={self.code}"
    
    
    def get_short_description(self, max_length: int = 100) -> str:
        """Qisqacha tavsif olish"""
        if not self.description:
            return "Tavsif mavjud emas"
        
        if len(self.description) <= max_length:
            return self.description
        
        return self.description[:max_length-3] + "..."


@dataclass
class Channel:
    """Kanal modeli"""
    id: Optional[int] = None
    channel_id: Optional[int] = None  # Telegram channel ID
    title: str = ""
    channel_link: str = ""
    channel_username: str = ""
    status: ChannelStatus = ChannelStatus.AKTIV
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if isinstance(self.status, str):
            self.status = ChannelStatus(self.status)
    
    @classmethod
    def from_record(cls, record) -> 'Channel':
        """Database record dan Channel obyekti yaratish"""
        if not record:
            return None
        
        return cls(
            id=record['id'],
            channel_id=record.get('channel_id'),
            title=record['title'],
            channel_link=record['channel_link'],
            channel_username=record.get('channel_username', ''),
            status=ChannelStatus(record['status']),
            created_at=record['created_at']
        )
    
    def to_dict(self) -> dict:
        """Channel obyektini dict ga aylantirish"""
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'title': self.title,
            'channel_link': self.channel_link,
            'channel_username': self.channel_username,
            'status': self.status.value,
            'created_at': self.created_at
        }
    
    def get_identifier(self) -> Union[int, str]:
        """Kanal identifikatorini olish (ID yoki username)"""
        if self.channel_id:
            return self.channel_id
        elif self.channel_username:
            return self.channel_username.lstrip('@')
        else:
            return self.channel_link.split('/')[-1]
        
    def is_active(self) -> bool:
        """Kanalning faol holatini tekshirish"""
        return self.status == ChannelStatus.AKTIV


@dataclass
class JoinedUserChannel:
    """Foydalanuvchi-Kanal bog'lanish modeli"""
    id: Optional[int] = None
    user_id: int = 0
    channel_id: int = 0
    joined_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.joined_at is None:
            self.joined_at = datetime.now()
    
    @classmethod
    def from_record(cls, record) -> 'JoinedUserChannel':
        """Database record dan JoinedUserChannel obyekti yaratish"""
        if not record:
            return None
        
        return cls(
            id=record['id'],
            user_id=record['user_id'],
            channel_id=record['channel_id'],
            joined_at=record['joined_at']
        )
    
    def to_dict(self) -> dict:
        """JoinedUserChannel obyektini dict ga aylantirish"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'channel_id': self.channel_id,
            'joined_at': self.joined_at
        }


@dataclass
class MovieView:
    """Kino ko'rish modeli"""
    id: Optional[int] = None
    user_id: int = 0
    movie_id: int = 0
    viewed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.viewed_at is None:
            self.viewed_at = datetime.now()
    
    @classmethod
    def from_record(cls, record) -> 'MovieView':
        """Database record dan MovieView obyekti yaratish"""
        if not record:
            return None
        
        return cls(
            id=record['id'],
            user_id=record['user_id'],
            movie_id=record['movie_id'],
            viewed_at=record['viewed_at']
        )
    
    def to_dict(self) -> dict:
        """MovieView obyektini dict ga aylantirish"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'viewed_at': self.viewed_at
        }


# Helper classes for complex queries
@dataclass
class UserChannelInfo:
    """Foydalanuvchi va kanal ma'lumotlari"""
    user: User
    channels: List[Channel]
    joined_channels: List[int]  # joined channel IDs
    
    def get_unjoined_channels(self) -> List[Channel]:
        """Obuna bo'lmagan kanallar ro'yxati"""
        return [ch for ch in self.channels if ch.id not in self.joined_channels]
    
    def is_subscribed_to_all(self) -> bool:
        """Barcha kanallarga obuna bo'lgan yoki yo'qligini tekshirish"""
        active_channels = [ch for ch in self.channels if ch.is_active()]
        return len(self.get_unjoined_channels()) == 0


@dataclass
class MovieStats:
    """Kino statistikasi"""
    movie: Movie
    total_views: int
    unique_viewers: int
    recent_views: int  # oxirgi 24 soat ichida
    
    def get_popularity_score(self) -> float:
        """Mashhurlik ballini hisoblash"""
        if self.total_views == 0:
            return 0.0
        
        # Unique viewers / total views ratio + recent activity bonus
        uniqueness_ratio = self.unique_viewers / self.total_views
        recent_bonus = min(self.recent_views / 10, 1.0)  # max 1.0 bonus
        
        return (uniqueness_ratio * 0.7) + (recent_bonus * 0.3)


@dataclass
class UserActivity:
    """Foydalanuvchi faoliyati"""
    user: User
    total_movies_watched: int
    favorite_genres: List[str]
    last_activity: datetime
    activity_score: float
    
    def is_active_user(self) -> bool:
        """Faol foydalanuvchi ekanligini tekshirish"""
        return self.activity_score > 0.5 and self.total_movies_watched > 0