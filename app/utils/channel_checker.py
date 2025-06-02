"""
Kanal obuna tekshirish yordamchi funksiyalar
"""

from typing import List
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from app.database.models import Channel


async def check_user_channel_subscription(bot: Bot, user_id: int, channel_id: int) -> bool:
    """
    Foydalanuvchining kanalga obuna bo'lganligini Telegram channel ID orqali tekshirish
    
    Args:
        bot: Bot instance
        user_id: Telegram foydalanuvchi ID
        channel_id: Telegram kanal ID
    
    Returns:
        bool: Obuna bo'lgan yoki yo'qligi
    """
    
    try:
        # Foydalanuvchi a'zoligini tekshirish
        member = await bot.get_chat_member(
            chat_id=channel_id,
            user_id=user_id
        )
        
        # A'zolik holatini tekshirish
        # creator, administrator, member - obuna bo'lgan
        # left, kicked - obuna bo'lmagan
        return member.status in ['creator', 'administrator', 'member']
        
    except (TelegramBadRequest, TelegramForbiddenError) as e:
        # Kanal mavjud emas yoki bot admin emas
        print(f"Channel check error for {channel_id}: {e}")
        return False
    
    except Exception as e:
        print(f"Unexpected error checking subscription to {channel_id}: {e}")
        return False


async def check_multiple_channels_subscription(bot: Bot, user_id: int, channels: List[Channel]) -> dict:
    """
    Bir nechta kanalga obuna holatini tekshirish
    
    Args:
        bot: Bot instance
        user_id: Telegram foydalanuvchi ID
        channels: Kanallar ro'yxati
    
    Returns:
        dict: Obuna holati ma'lumotlari
    """
    
    subscribed_channels = []
    unsubscribed_channels = []
    error_channels = []
    
    for channel in channels:
        if not channel.is_active():
            continue
        
        try:
            is_subscribed = await check_user_channel_subscription(
                bot, user_id, channel.get_username_clean()
            )
            
            if is_subscribed:
                subscribed_channels.append(channel)
            else:
                unsubscribed_channels.append(channel)
                
        except Exception as e:
            print(f"Error checking channel {channel.title}: {e}")
            error_channels.append(channel)
    
    return {
        'subscribed': subscribed_channels,
        'unsubscribed': unsubscribed_channels,
        'errors': error_channels,
        'is_fully_subscribed': len(unsubscribed_channels) == 0
    }


async def get_unsubscribed_channels_text(content_name: str, channels: List[Channel]) -> str:
    """
    Obuna bo'lmagan kanallar uchun xabar matni yaratish
    
    Args:
        content_name: Kontent nomi (masalan, kino nomi)
        channels: Obuna bo'lmagan kanallar ro'yxati
    
    Returns:
        str: Formatlanган xabar matni
    """
    
    if not channels:
        return f"✅ Siz barcha kanallarga obuna bo'lgansiz! {content_name}ni tomosha qilishingiz mumkin."
    
    text = f"""
⚠️ <b>Obuna Talab Qilinadi</b>

🎬 <b>{content_name}</b>ni tomosha qilish uchun quyidagi kanallarga obuna bo'lishingiz shart!

📺 <b>Obuna bo'lish kerak:</b>
"""
    
    for i, channel in enumerate(channels, 1):
        text += f"\n{i}. <a href='{channel.channel_link}'>{channel.title}</a>"
    
    text += f"""

💡 <b>Qo'llanma:</b>
1. Yuqoridagi kanallarga obuna bo'ling
2. "✅ Obunani tekshirish" tugmasini bosing
3. {content_name}dan zavqlaning!

⚠️ <b>Muhim:</b> Barcha kanallarga obuna bo'lmasangiz, kino yuborilmaydi.
"""
    
    return text


def format_subscription_status(subscribed_count: int, total_count: int) -> str:
    """
    Obuna holatini formatlash
    
    Args:
        subscribed_count: Obuna bo'lgan kanallar soni
        total_count: Jami kanallar soni
    
    Returns:
        str: Formatlanган holat
    """
    
    if subscribed_count == total_count:
        return "✅ Barcha kanallarga obuna"
    elif subscribed_count == 0:
        return "❌ Hech qaysi kanalga obuna emas"
    else:
        return f"⚠️ {subscribed_count}/{total_count} kanalga obuna"


def get_subscription_progress_bar(subscribed_count: int, total_count: int, width: int = 10) -> str:
    """
    Obuna jarayonining progress bar yaratish
    
    Args:
        subscribed_count: Obuna bo'lgan kanallar soni
        total_count: Jami kanallar soni
        width: Progress bar kengligi
    
    Returns:
        str: Progress bar
    """
    
    if total_count == 0:
        return "▪️" * width
    
    progress = subscribed_count / total_count
    filled = int(progress * width)
    empty = width - filled
    
    return "🟩" * filled + "⬜" * empty


async def validate_channel_access(bot: Bot, channel_username: str) -> dict:
    """
    Botning kanalga kirish huquqini tekshirish
    
    Args:
        bot: Bot instance
        channel_username: Kanal username
    
    Returns:
        dict: Tekshirish natijalari
    """
    
    try:
        # @ belgisini qo'shish
        if not channel_username.startswith('@'):
            channel_username = '@' + channel_username
        
        # Bot kanalga kira oladimi
        chat = await bot.get_chat(channel_username)
        
        # Bot a'zolik holatini tekshirish
        bot_member = await bot.get_chat_member(channel_username, bot.id)
        
        return {
            'accessible': True,
            'chat_title': chat.title,
            'chat_type': chat.type,
            'bot_status': bot_member.status,
            'can_check_members': bot_member.status in ['creator', 'administrator'],
            'error': None
        }
        
    except TelegramBadRequest as e:
        return {
            'accessible': False,
            'error': f"Bad request: {e}",
            'suggestion': "Kanal username ini tekshiring"
        }
    
    except TelegramForbiddenError as e:
        return {
            'accessible': False,
            'error': f"Forbidden: {e}",
            'suggestion': "Botni kanalga admin qiling"
        }
    
    except Exception as e:
        return {
            'accessible': False,
            'error': f"Unknown error: {e}",
            'suggestion': "Kanal sozlamalarini tekshiring"
        }


def get_channel_invite_text(channel: Channel) -> str:
    """
    Kanal taklif matni yaratish
    
    Args:
        channel: Kanal obyekti
    
    Returns:
        str: Taklif matni
    """
    
    return f"""
📺 <b>{channel.title}</b>

🔗 Kanal: {channel.channel_link}

💡 <b>Nima uchun obuna bo'lish kerak?</b>
• Eng yangi kinolar haqida xabar olish
• Eksklyuziv kontentlar
• Kinematika jamiyatining a'zosi bo'lish

👆 Yuqoridagi havolaga bosib, "OBUNA BO'LISH" tugmasini bosing!
"""


async def auto_check_and_update_subscriptions(bot: Bot, user_id: int, db_queries, channels: List[Channel]) -> dict:
    """
    Obunalarni avtomatik tekshirish va ma'lumotlar bazasini yangilash
    
    Args:
        bot: Bot instance
        user_id: Telegram foydalanuvchi ID
        db_queries: Database queries instance
        channels: Tekshirish uchun kanallar
    
    Returns:
        dict: Yangilash natijalari
    """
    
    user = await db_queries.get_user_by_tg_id(user_id)
    if not user:
        return {'error': 'User not found'}
    
    updated_channels = []
    failed_channels = []
    
    for channel in channels:
        try:
            is_subscribed = await check_user_channel_subscription(
                bot, user_id, channel.get_username_clean()
            )
            
            if is_subscribed:
                # Ma'lumotlar bazasiga qo'shish
                await db_queries.add_user_to_channel(user.id, channel.id)
                updated_channels.append(channel)
            else:
                # Ma'lumotlar bazasidan olib tashlash
                await db_queries.remove_user_from_channel(user.id, channel.id)
                
        except Exception as e:
            print(f"Auto check failed for {channel.title}: {e}")
            failed_channels.append({'channel': channel, 'error': str(e)})
    
    return {
        'updated': updated_channels,
        'failed': failed_channels,
        'success_count': len(updated_channels),
        'error_count': len(failed_channels)
    }