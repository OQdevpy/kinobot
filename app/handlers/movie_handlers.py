"""
Kino bilan bog'liq handlerlar
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from app.database import DatabaseQueries
from app.filters.movie_code_filter import MovieCodeFilter
from app.filters.channel_filter import ChannelSubscriptionFilter
from app.keyboards.inline_keyboards import get_movie_keyboard, get_subscription_keyboard
from app.utils.movie_manager import send_movie_to_user, check_movie_access
from app.utils.channel_checker import get_unsubscribed_channels_text

router = Router()


@router.message(MovieCodeFilter(), ChannelSubscriptionFilter())
async def movie_request_handler(message: Message):
    """Kino kodini ishlov berish (obuna bo'lgan foydalanuvchilar uchun)"""
    
    movie_code = message.text.strip().upper()
    db_queries = DatabaseQueries()
    
    try:
        # Kinoni topish
        movie = await db_queries.get_movie_by_code(movie_code)
        
        if not movie:
            await message.answer(
                f"❌ <b>Kino topilmadi</b>\n\n"
                f"🔍 <code>{movie_code}</code> kodi bo'yicha kino mavjud emas.\n\n"
                f"💡 <b>Tavsiyalar:</b>\n"
                f"• Kodni to'g'ri yozganingizni tekshiring\n"
                f"• Katta harflar bilan yozing\n"
                f"• Mashhur kinolar ro'yxatini ko'ring",
                parse_mode="HTML"
            )
            return
        
        # Foydalanuvchini aniqlash
        user = await db_queries.get_user_by_tg_id(message.from_user.id)
        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi. /start bosing.")
            return
        
        # Kino yuborish
        await send_movie_to_user(message, movie, user, db_queries)
        
    except Exception as e:
        await message.answer("❌ Kino yuklashda xatolik yuz berdi.")
        print(f"Movie request error: {e}")


@router.message(MovieCodeFilter())
async def movie_request_no_subscription_handler(message: Message):
    """Kino kodini ishlov berish (obuna bo'lmagan foydalanuvchilar uchun)"""
    
    movie_code = message.text.strip().upper()
    db_queries = DatabaseQueries()
    
    try:
        # Kinoni tekshirish
        movie = await db_queries.get_movie_by_code(movie_code)
        
        if not movie:
            await message.answer(
                f"❌ <code>{movie_code}</code> kodi bo'yicha kino topilmadi.",
                parse_mode="HTML"
            )
            return
        
        # Foydalanuvchini aniqlash
        user = await db_queries.get_user_by_tg_id(message.from_user.id)
        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi. /start bosing.")
            return
        
        # Obuna holatini tekshirish
        subscription_info = await db_queries.check_user_subscription(user.id)
        unsubscribed_channels = subscription_info.get_unjoined_channels()
        
        if unsubscribed_channels:
            # Obuna bo'lmagan kanallar haqida xabar
            subscription_text = await get_unsubscribed_channels_text(
                movie.title, 
                unsubscribed_channels
            )
            
            keyboard = get_subscription_keyboard(unsubscribed_channels)
            
            await message.answer(
                subscription_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            # Bu holat bo'lmasligi kerak, lekin xavfsizlik uchun
            await send_movie_to_user(message, movie, user, db_queries)
        
    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi.")
        print(f"Movie no subscription error: {e}")


@router.callback_query(F.data.startswith("watch_movie:"))
async def watch_movie_handler(callback: CallbackQuery):
    """Kino tomosha qilish tugmasi"""
    await callback.answer()
    
    try:
        movie_id = int(callback.data.split(":")[1])
        
        db_queries = DatabaseQueries()
        
        # Kinoni topish
        movie = await db_queries.get_movie_by_id(movie_id)
        if not movie:
            await callback.message.edit_text("❌ Kino topilmadi.")
            return
        
        # Foydalanuvchini aniqlash
        user = await db_queries.get_user_by_tg_id(callback.from_user.id)
        if not user:
            await callback.message.edit_text("❌ Foydalanuvchi topilmadi.")
            return
        
        # Obuna holatini qayta tekshirish
        subscription_info = await db_queries.check_user_subscription(user.id)
        
        if not subscription_info.is_subscribed_to_all():
            unsubscribed_channels = subscription_info.get_unjoined_channels()
            subscription_text = await get_unsubscribed_channels_text(
                movie.title, 
                unsubscribed_channels
            )
            
            keyboard = get_subscription_keyboard(unsubscribed_channels)
            
            await callback.message.edit_text(
                subscription_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            return
        
        # Kinoni yuborish
        await send_movie_to_user(callback.message, movie, user, db_queries)
        
    except Exception as e:
        await callback.message.edit_text("❌ Kino yuklashda xatolik.")
        print(f"Watch movie error: {e}")


@router.callback_query(F.data.startswith("movie_info:"))
async def movie_info_handler(callback: CallbackQuery):
    """Kino haqida ma'lumot"""
    await callback.answer()
    
    try:
        movie_id = int(callback.data.split(":")[1])
        
        db_queries = DatabaseQueries()
        movie = await db_queries.get_movie_by_id(movie_id)
        
        if not movie:
            await callback.message.edit_text("❌ Kino topilmadi.")
            return
        
        # Kino statistikasi
        stats = await db_queries.get_movie_stats(movie_id)
        
        info_text = f"""
🎬 <b>{movie.title}</b>

📝 <b>Kod:</b> <code>{movie.code}</code>
🆔 <b>ID:</b> {movie.id}

📖 <b>Tavsif:</b>
{movie.description or 'Tavsif mavjud emas'}

📊 <b>Statistika:</b>
• Jami ko'rishlar: {stats.total_views if stats else movie.view_count}
• Noyob tomoshabinlar: {stats.unique_viewers if stats else "Noma'lum"}
• Oxirgi 24 soat: {stats.recent_views if stats else "Noma'lum"}
• Mashhurlik ball: {stats.get_popularity_score():.2f if stats else "Noma'lum"}

📅 <b>Qo'shilgan:</b> {movie.created_at.strftime('%Y-%m-%d %H:%M')}

💡 <b>Ko'rish uchun kodni yuboring:</b> <code>{movie.code}</code>
"""
        
        keyboard = get_movie_keyboard(movie)
        
        await callback.message.edit_text(
            info_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.message.edit_text("❌ Ma'lumot yuklashda xatolik.")
        print(f"Movie info error: {e}")


@router.callback_query(F.data.startswith("share_movie:"))
async def share_movie_handler(callback: CallbackQuery):
    """Kinoni ulashish"""
    await callback.answer("📤 Ulashish ma'lumotlari tayyorlanmoqda...")
    
    try:
        movie_id = int(callback.data.split(":")[1])
        
        db_queries = DatabaseQueries()
        movie = await db_queries.get_movie_by_id(movie_id)
        
        if not movie:
            await callback.answer("❌ Kino topilmadi.", show_alert=True)
            return
        
        # Bot username ni olish (real botda o'zgaradi)
        bot_username = "kinematika_bot"  # Bu qiymatni configdan olish kerak
        
        share_text = f"""
🎬 <b>{movie.title}</b>

📝 Kod: <code>{movie.code}</code>

🤖 Bot: @{bot_username}

💬 <b>Ulashish matni:</b>

🎬 {movie.title} filmini tomosha qiling!

📝 Kod: {movie.code}
🤖 Bot: @{bot_username}

Ko'rish uchun botga kirib, kodini yuboring! 🍿
"""
        
        await callback.message.answer(share_text, parse_mode="HTML")
        
    except Exception as e:
        await callback.answer("❌ Ulashish xatoligi.", show_alert=True)
        print(f"Share movie error: {e}")


@router.callback_query(F.data.startswith("rate_movie:"))
async def rate_movie_handler(callback: CallbackQuery):
    """Kinoni baholash (kelajakda qo'shilishi mumkin)"""
    await callback.answer("⭐ Baholash tizimi tez orada qo'shiladi!", show_alert=True)


@router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: CallbackQuery):
    """Obuna holatini qayta tekshirish"""
    await callback.answer("🔄 Obuna holati tekshirilmoqda...")
    
    try:
        db_queries = DatabaseQueries()
        user = await db_queries.get_user_by_tg_id(callback.from_user.id)
        
        if not user:
            await callback.message.edit_text("❌ Foydalanuvchi topilmadi.")
            return
        
        # Obuna holatini tekshirish
        subscription_info = await db_queries.check_user_subscription(user.id)
        
        if subscription_info.is_subscribed_to_all():
            await callback.message.edit_text(
                "✅ <b>Ajoyib!</b>\n\n"
                "Siz barcha majburiy kanallarga obuna bo'lgansiz.\n"
                "Endi kinolarni to'liq tomosha qilishingiz mumkin! 🎬\n\n"
                "🎯 Kino kodini yuboring yoki menyudan tanlang.",
                parse_mode="HTML"
            )
        else:
            unsubscribed_channels = subscription_info.get_unjoined_channels()
            subscription_text = await get_unsubscribed_channels_text(
                "kinolar", 
                unsubscribed_channels
            )
            
            keyboard = get_subscription_keyboard(unsubscribed_channels)
            
            await callback.message.edit_text(
                subscription_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
    
    except Exception as e:
        await callback.message.edit_text("❌ Tekshirishda xatolik.")
        print(f"Check subscription error: {e}")


@router.message(F.text.regexp(r'^[A-Z0-9_]{3,20}$'))
async def possible_movie_code_handler(message: Message):
    """Mumkin bo'lgan kino kodi (backup handler)"""
    
    # Bu handler oxirgi bo'lib ishga tushadi
    possible_code = message.text.strip().upper()
    
    db_queries = DatabaseQueries()
    
    try:
        # Kinoni tekshirish
        movie = await db_queries.get_movie_by_code(possible_code)
        
        if movie:
            # Agar kino mavjud bo'lsa, asosiy handlerlarga yo'naltirish
            await movie_request_handler(message)
        else:
            # Kino topilmasa, yordam berish
            help_text = f"""
🤔 <b>"{possible_code}" kodi bo'yicha kino topilmadi</b>

💡 <b>Tavsiyalar:</b>
• Kodni to'g'ri yozganingizni tekshiring
• Mashhur kinolar ro'yxatini ko'ring
• Qidirish funksiyasidan foydalaning

📋 Menyu tugmasini bosib, boshqa variantlarni ko'ring.
"""
            
            await message.answer(help_text, parse_mode="HTML")
    
    except Exception as e:
        print(f"Possible movie code handler error: {e}")


def register_movie_handlers(dp):
    """Movie handlerlarni ro'yxatga olish"""
    dp.include_router(router)