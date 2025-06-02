"""
Reply klaviaturalar
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove


def get_main_reply_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy reply klaviatura"""
    
    buttons = [
        [
            KeyboardButton(text="🔍 Qidirish"),
            KeyboardButton(text="📊 Mashhur kinolar")
        ],
        [
            KeyboardButton(text="🆕 Yangi kinolar"),
            KeyboardButton(text="📺 Kanallar")
        ],
        [
            KeyboardButton(text="📝 Mening tarixim"),
            KeyboardButton(text="📊 Statistika")
        ],
        [
            KeyboardButton(text="📋 Menyu"),
            KeyboardButton(text="ℹ️ Yordam")
        ]
    ]
    
    if is_admin:
        buttons.append([KeyboardButton(text="👑 Admin Panel")])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        row_width=2
    )


def get_admin_reply_keyboard() -> ReplyKeyboardMarkup:
    """Admin reply klaviatura"""
    
    buttons = [
        [
            KeyboardButton(text="🎬 Kinolar"),
            KeyboardButton(text="📺 Kanallar")
        ],
        [
            KeyboardButton(text="👥 Foydalanuvchilar"),
            KeyboardButton(text="📊 Admin Statistika")
        ],
        [
            KeyboardButton(text="📤 Ma'lumot eksport"),
            KeyboardButton(text="🛠 Sozlamalar")
        ],
        [
            KeyboardButton(text="📋 Asosiy Menyu"),
            KeyboardButton(text="👤 Foydalanuvchi rejimi")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        row_width=2
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish klaviaturasi"""
    
    buttons = [
        [KeyboardButton(text="❌ Bekor qilish")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_skip_keyboard() -> ReplyKeyboardMarkup:
    """O'tkazib yuborish klaviaturasi"""
    
    buttons = [
        [
            KeyboardButton(text="⏩ O'tkazib yuborish"),
            KeyboardButton(text="❌ Bekor qilish")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_yes_no_keyboard() -> ReplyKeyboardMarkup:
    """Ha/Yo'q klaviaturasi"""
    
    buttons = [
        [
            KeyboardButton(text="✅ Ha"),
            KeyboardButton(text="❌ Yo'q")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def remove_keyboard() -> ReplyKeyboardRemove:
    """Klaviaturani olib tashlash"""
    return ReplyKeyboardRemove()