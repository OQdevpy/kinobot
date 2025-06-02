"""
Inline klaviaturalar
"""

from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.database.models import Movie, Channel


def get_main_menu_keyboard(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Asosiy menyu klaviaturasi"""
    
    buttons = [
        [InlineKeyboardButton(text="🔍 Qidirish", callback_data="search_movies")],
        [
            InlineKeyboardButton(text="📊 Mashhur", callback_data="popular_movies"),
            InlineKeyboardButton(text="🆕 Yangi", callback_data="recent_movies")
        ],
        [InlineKeyboardButton(text="📺 Kanallar", callback_data="channels_list")],
        [InlineKeyboardButton(text="📝 Tarixim", callback_data="my_history")]
    ]
    
    if is_admin:
        buttons.append([InlineKeyboardButton(text="👑 Admin Panel", callback_data="admin_panel")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Admin asosiy menyu"""
    
    buttons = [
        [
            InlineKeyboardButton(text="🎬 Kinolar", callback_data="admin_movies"),
            InlineKeyboardButton(text="📺 Kanallar", callback_data="admin_channels")
        ],
        [
            InlineKeyboardButton(text="👥 Foydalanuvchilar", callback_data="admin_users"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_statistics")
        ],
        [InlineKeyboardButton(text="📤 Eksport", callback_data="export_data")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_movie_keyboard() -> InlineKeyboardMarkup:
    """Admin kino boshqaruvi klaviaturasi"""
    
    buttons = [
        [InlineKeyboardButton(text="➕ Kino qo'shish", callback_data="add_movie")],
        [
            InlineKeyboardButton(text="🔍 Qidirish", callback_data="admin_search_movies"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="movies_statistics")
        ],
        [
            InlineKeyboardButton(text="🗑 O'chirish", callback_data="delete_movie"),
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="edit_movie")
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_channel_keyboard() -> InlineKeyboardMarkup:
    """Admin kanal boshqaruvi klaviaturasi"""
    
    buttons = [
        [InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel")],
        [
            InlineKeyboardButton(text="⚙️ Boshqarish", callback_data="manage_channels"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="channels_statistics")
        ],
        [
            InlineKeyboardButton(text="🔴 O'chirish", callback_data="deactivate_channel"),
            InlineKeyboardButton(text="🟢 Faollashtirish", callback_data="activate_channel")
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_users_keyboard() -> InlineKeyboardMarkup:
    """Admin foydalanuvchilar boshqaruvi"""
    
    buttons = [
        [
            InlineKeyboardButton(text="🔍 Qidirish", callback_data="search_users"),
            InlineKeyboardButton(text="📊 Statistika", callback_data="users_statistics")
        ],
        [
            InlineKeyboardButton(text="👑 Admin qilish", callback_data="make_admin"),
            InlineKeyboardButton(text="📤 Eksport", callback_data="export_users")
        ],
        [
            InlineKeyboardButton(text="📢 Xabar yuborish", callback_data="broadcast_message"),
            InlineKeyboardButton(text="🚫 Bloklash", callback_data="block_user")
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_panel")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_movie_search_keyboard(movies: List[Movie]) -> InlineKeyboardMarkup:
    """Kino qidirish natijalari klaviaturasi"""
    
    buttons = []
    
    for movie in movies[:10]:  # Maksimal 10 ta kino
        buttons.append([InlineKeyboardButton(
            text=f"🎬 {movie.title}",
            callback_data=f"movie_detail:{movie.id}"
        )])
    
    # Boshqarish tugmalari
    if len(movies) > 10:
        buttons.append([
            InlineKeyboardButton(text="⬅️ Oldingi", callback_data="page:prev"),
            InlineKeyboardButton(text="➡️ Keyingi", callback_data="page:next")
        ])
    
    buttons.append([InlineKeyboardButton(text="🔙 Menyu", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_movie_detail_keyboard(movie: Movie) -> InlineKeyboardMarkup:
    """Kino tafsilotlari klaviaturasi"""
    
    buttons = [
        [InlineKeyboardButton(text="🎬 Tomosha qilish", callback_data=f"watch_movie:{movie.id}")],
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data=f"movie_stats:{movie.id}"),
            InlineKeyboardButton(text="📤 Ulashish", callback_data=f"share_movie:{movie.id}")
        ],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_search")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_movie_keyboard(movie: Movie) -> InlineKeyboardMarkup:
    """Kino klaviaturasi (asosiy)"""
    
    buttons = [
        [InlineKeyboardButton(text="🎬 Tomosha qilish", callback_data=f"watch_movie:{movie.id}")],
        [
            InlineKeyboardButton(text="ℹ️ Ma'lumot", callback_data=f"movie_info:{movie.id}"),
            InlineKeyboardButton(text="📤 Ulashish", callback_data=f"share_movie:{movie.id}")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subscription_keyboard(channels: List[Channel]) -> InlineKeyboardMarkup:
    """Obuna klaviaturasi"""
    
    buttons = []
    
    # Har bir kanal uchun tugma
    for channel in channels[:5]:  # Maksimal 5 ta kanal
        buttons.append([InlineKeyboardButton(
            text=f"📺 {channel.title}",
            callback_data=f"join_channel:{channel.id}"
        )])
    
    # Umumiy tugmalar
    buttons.append([InlineKeyboardButton(
        text="📺 Barcha kanallarga obuna",
        callback_data="join_all_channels"
    )])
    
    buttons.append([InlineKeyboardButton(
        text="✅ Obunani tekshirish",
        callback_data="check_subscription"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_channels_list_keyboard(channels: List[Channel]) -> InlineKeyboardMarkup:
    """Kanallar ro'yxati klaviaturasi"""
    
    buttons = []
    
    # Har bir kanal uchun tugma
    for channel in channels:
        buttons.append([InlineKeyboardButton(
            text=f"📺 {channel.title}",
            url=channel.channel_link
        )])
    
    buttons.append([InlineKeyboardButton(
        text="✅ Obunani tekshirish",
        callback_data="check_subscription"
    )])
    
    buttons.append([InlineKeyboardButton(text="🔙 Menyu", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirmation_keyboard(confirm_data: str, cancel_data: str) -> InlineKeyboardMarkup:
    """Tasdiqlash klaviaturasi"""
    
    buttons = [
        [
            InlineKeyboardButton(text="✅ Ha", callback_data=confirm_data),
            InlineKeyboardButton(text="❌ Yo'q", callback_data=cancel_data)
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_pagination_keyboard(page_type: str, current_page: int, total_pages: int, items: List) -> InlineKeyboardMarkup:
    """Sahifalash klaviaturasi"""
    
    buttons = []
    
    # Elementlar tugmalari
    for item in items:
        if hasattr(item, 'title'):  # Movie yoki Channel
            buttons.append([InlineKeyboardButton(
                text=f"🎬 {item.title}",
                callback_data=f"item_detail:{item.id}"
            )])
    
    # Sahifalash tugmalari
    nav_buttons = []
    
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Oldingi",
            callback_data=f"page:{page_type}:{current_page-1}"
        ))
    
    nav_buttons.append(InlineKeyboardButton(
        text=f"{current_page}/{total_pages}",
        callback_data="current_page"
    ))
    
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(
            text="➡️ Keyingi", 
            callback_data=f"page:{page_type}:{current_page+1}"
        ))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([InlineKeyboardButton(text="🔙 Menyu", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)



def get_movie_subscription_keyboard(channels: List, movie_code: str) -> InlineKeyboardMarkup:
    """Kino uchun obuna klaviaturasi"""
    
    buttons = []
    
    # Har bir kanal uchun tugma
    for channel in channels[:5]:  # Maksimal 5 ta kanal
        buttons.append([InlineKeyboardButton(
            text=f"📺 {channel.title}",
            url=channel.channel_link
        )])
    
    # Obunani tekshirish tugmasi - movie code bilan
    buttons.append([InlineKeyboardButton(
        text="✅ Obunani tekshirish",
        callback_data=f"check_subscription_for_movie:{movie_code}"
    )])
    
    # Orqaga tugmasi
    buttons.append([InlineKeyboardButton(
        text="🔙 Bosh sahifa",
        callback_data="back_to_main"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_subscription_required_keyboard(channels: List) -> InlineKeyboardMarkup:
    """Umumiy obuna talab qilingan klaviatura"""
    
    buttons = []
    
    # Barcha kanallarga obuna tugmasi
    if len(channels) > 1:
        buttons.append([InlineKeyboardButton(
            text="📺 Barcha kanallarga obuna",
            callback_data="join_all_channels"
        )])
    
    # Har bir kanal uchun tugma
    for channel in channels[:3]:  # Maksimal 3 ta kanal
        buttons.append([InlineKeyboardButton(
            text=f"📺 {channel.title}",
            url=channel.channel_link
        )])
    
    # Umumiy tekshirish
    buttons.append([InlineKeyboardButton(
        text="✅ Obunani tekshirish",
        callback_data="check_subscription"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)