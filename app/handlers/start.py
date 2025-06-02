"""
Start komandasi handleri - Kino kod bilan va kodsiz
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from typing import List

from app.database import DatabaseQueries
from app.keyboards.inline_keyboards import (
    get_main_menu_keyboard,
    get_movie_subscription_keyboard,
    get_subscription_required_keyboard
)
from app.keyboards.reply_keyboards import get_main_reply_keyboard
from app.utils.channel_checker import check_user_channel_subscription
from app.utils.movie_manager import send_movie_to_user, send_movie_to_user_from_private

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Start komandasi handleri - kod bilan yoki kodsiz"""
    await state.clear()
    
    db_queries = DatabaseQueries()
    
    try:
        # Foydalanuvchini ro'yxatdan o'tkazish yoki yangilash
        user = await db_queries.create_user(
            tg_id=message.from_user.id,
            full_name=message.from_user.full_name or "Noma'lum",
            is_admin=False
        )
        
        # Start parametrini tekshirish (kino kodi)
        start_param = message.text.split()
        
        if len(start_param) > 1 and start_param[1]:
            # Kino kodi bilan start
            print(f"Start with movie code: {start_param[1]}")
            movie_code = start_param[1].upper()
            await handle_movie_request_with_code(message, user, movie_code, db_queries)
        else:
            # Oddiy start
            await handle_regular_start(message, user)
        
    except Exception as e:
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.\n\n"
            "Agar muammo davom etsa, admin bilan bog'laning."
        )
        print(f"Start handler error: {e}")


async def handle_movie_request_with_code(message: Message, user, movie_code: str, db_queries):
    """Kino kodi bilan start qilinganda"""
    
    try:
        # Kinoni topish
        movie = await db_queries.get_movie_by_code(movie_code)
        
        if not movie:
            await message.answer(
                f"❌ <b>Kino topilmadi</b>\n\n"
                f"🔍 <code>{movie_code}</code> kodi bo'yicha kino mavjud emas.\n\n"
                f"💡 Kodni to'g'ri yozganingizni tekshiring yoki boshqa filmlar uchun /menu bosing.",
                parse_mode="HTML"
            )
            return
        
        # Obuna holatini tekshirish
        subscription_info = await db_queries.get_active_channels()
        print(f"Subscription info: {subscription_info}")
        
        unsubscribed_channels = []
        for channel in subscription_info:
            is_subscribed = await check_user_channel_subscription(
                message.bot, user.tg_id, channel.channel_id
            )
            if not is_subscribed:
                unsubscribed_channels.append(channel)
        
        if unsubscribed_channels:
            # Obuna bo'lmagan kanallar bor
            await send_subscription_required_message(message, movie, unsubscribed_channels)
        else:
            # Barcha kanallarga obuna bo'lgan
            await send_movie_to_user_from_private(message, movie, user, db_queries)
        
    except Exception as e:
        await message.answer("❌ Kino yuklashda xatolik yuz berdi.")
        print(f"Movie request with code error: {e}")


async def send_subscription_required_message(message: Message, movie, unsubscribed_channels):
    """Obuna talab qilingan xabar yuborish"""
    
    subscription_text = f"""
🎬 <b>{movie.title}</b>

⚠️ <b>Obuna Talab Qilinadi!</b>

Bu kinoni tomosha qilish uchun quyidagi kanallarga obuna bo'lishingiz shart:

📺 <b>Obuna bo'ling:</b>
"""
    
    for i, channel in enumerate(unsubscribed_channels, 1):
        subscription_text += f"\n{i}. <a href='{channel.channel_link}'>{channel.title}</a>"
    
    subscription_text += f"""

💡 <b>Qo'llanma:</b>
1. Yuqoridagi barcha kanallarga obuna bo'ling
2. "✅ Obunani tekshirish" tugmasini bosing
3. {movie.title} filmidan zavqlaning!

⚠️ <b>Diqqat:</b> Barcha kanallarga obuna bo'lmasangiz, kino yuborilmaydi.
"""
    
    keyboard = get_movie_subscription_keyboard(unsubscribed_channels, movie.code)
    
    await message.answer(
        subscription_text,
        reply_markup=keyboard,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


async def handle_regular_start(message: Message, user):
    """Oddiy start (kodsiz)"""
    
    is_admin = user.is_admin
    
    # Xush kelibsiz xabari
    welcome_text = f"""
🎬 <b>Kinematika Platformasiga Xush Kelibsiz!</b>

👋 Salom, <b>{user.full_name}</b>!

Bu bot orqali siz:
🎥 Kinolarni kod orqali tomosha qilishingiz
🔍 Kinolar qidirish va kashf etishingiz  
📊 Mashhur kontentni ko'rishingiz mumkin

🚀 <b>Boshlash uchun:</b>
• Kino kodini yuboring (masalan: DEMO001)
• Yoki quyidagi tugmalardan foydalaning

⚠️ <b>Muhim:</b> Barcha kinolarni tomosha qilish uchun majburiy kanallarga obuna bo'lishingiz shart!
"""
    
    if is_admin:
        welcome_text += "\n\n👑 <b>Admin huquqlari faol!</b>"
    
    # Klaviatura tanlash
    keyboard = get_main_menu_keyboard(is_admin=is_admin)
    reply_keyboard = get_main_reply_keyboard(is_admin=is_admin)
    
    await message.answer(
        text=welcome_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    # Reply klaviaturani ham qo'shish
    await message.answer(
        "Buyruqlarni tanlash uchun quyidagi tugmalardan foydalaning:",
        reply_markup=reply_keyboard
    )


@router.callback_query(F.data.startswith("check_subscription_for_movie:"))
async def check_subscription_for_movie_handler(callback: CallbackQuery):
        """Kino uchun obuna holatini tekshirish"""
        await callback.answer("🔄 Obuna holati tekshirilmoqda...")
        
    # try:
        # Callback data dan movie code ni olish
        movie_code = callback.data.split(":")[1]
        
        db_queries = DatabaseQueries()
        
        # Foydalanuvchini topish
        user = await db_queries.get_user_by_tg_id(callback.from_user.id)
        if not user:
            await callback.message.edit_text("❌ Foydalanuvchi topilmadi. /start bosing.")
            return
        
        # Kinoni topish
        movie = await db_queries.get_movie_by_code(movie_code)
        if not movie:
            await callback.message.edit_text("❌ Kino topilmadi.")
            return
        
        # Obuna holatini tekshirish
        subscription_info = await db_queries.get_active_channels()
        
        # Har bir kanalga real tekshirish (Telegram API orqali)
        unsubscribed_channels = []
        verified_channels = []
        
        for channel in subscription_info:
           
            # Agar channel_id mavjud bo'lsa, uni ishlatish
            if channel.channel_id:
                is_subscribed = await check_user_channel_subscription(
                    callback.bot, callback.from_user.id, channel.channel_id
                )
            else:
                is_subscribed = await check_user_channel_subscription(
                    callback.bot, callback.from_user.id, channel.channel_username
                )
            
            if is_subscribed:
                # Ma'lumotlar bazasini yangilash
                await db_queries.add_user_to_channel(user.id, channel.id)
                verified_channels.append(channel)
            else:
                unsubscribed_channels.append(channel)
        
        if not unsubscribed_channels:
            # Barcha kanallarga obuna bo'lgan - kinoni yuborish
            success_text = f"""
✅ <b>Ajoyib!</b>

Siz barcha majburiy kanallarga obuna bo'ldingiz!

🎬 <b>{movie.title}</b> filmi sizga yuborilmoqda...
"""
            await callback.message.edit_text(success_text, parse_mode="HTML")
            
            # Kinoni yuborish
            await send_movie_to_user_from_private(callback.message, movie, user, db_queries)
            
        else:
            # Ba'zi kanallarga obuna bo'lmagan
            partial_text = f"""
✅ <b>Obuna bo'ldi:</b> {len(verified_channels)} ta kanal

❌ <b>Qolgan kanallar:</b> {len(unsubscribed_channels)} ta

📋 <b>Hali obuna bo'lmagansiz:</b>
"""
            for channel in unsubscribed_channels:
                partial_text += f"• <a href='{channel.channel_link}'>{channel.title}</a>\n"
            
            partial_text += f"\n💡 Qolgan kanallarga ham obuna bo'ling va qayta tekshiring."
            
            keyboard = get_movie_subscription_keyboard(unsubscribed_channels, movie_code)
            
            await callback.message.edit_text(
                partial_text,
                reply_markup=keyboard,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        
    # except Exception as e:
    #     await callback.message.edit_text("❌ Tekshirishda xatolik yuz berdi.")
    #     print(f"Check subscription for movie error: {e}")


@router.message(Command("help"))
async def help_handler(message: Message):
    """Yordam komandasi"""
    
    help_text = """
🆘 <b>Yordam - Bot Foydalanish Qo'llanmasi</b>

<b>🎬 Asosiy Komandalar:</b>
/start - Botni qayta ishga tushirish
/help - Bu yordam xabari
/menu - Asosiy menyu

<b>🎥 Kino Tomosha Qilish:</b>
• Kino kodini to'g'ridan-to'g'ri yuboring
• Masalan: <code>DEMO001</code>

<b>🔍 Qidirish:</b>
• "🔍 Qidirish" tugmasini bosing
• Kino nomini yozing

<b>📊 Statistika:</b>
• "📊 Mashhur kinolar" - eng ko'p ko'rilgan kinolar
• "🆕 Yangi kinolar" - so'nggi qo'shilgan kinolar

<b>⚠️ Majburiy Obuna:</b>
Kinolarni tomosha qilish uchun barcha kanallarga obuna bo'lishingiz shart!

<b>🛠 Texnik Yordam:</b>
Muammolar bo'lsa admin bilan bog'laning: @admin_username
"""
    
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("menu"))
async def menu_handler(message: Message):
    """Asosiy menyu"""
    db_queries = DatabaseQueries()
    
    try:
        user = await db_queries.get_user_by_tg_id(message.from_user.id)
        is_admin = user.is_admin if user else False
        
        keyboard = get_main_menu_keyboard(is_admin=is_admin)
        
        menu_text = """
🎬 <b>Asosiy Menyu</b>

Quyidagi amallardan birini tanlang:
"""
        
        await message.answer(
            menu_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.answer("❌ Menyu yuklashda xatolik yuz berdi.")
        print(f"Menu handler error: {e}")


@router.message(F.text == "📋 Menyu")
async def reply_menu_handler(message: Message):
    """Reply klaviatura menyu tugmasi"""
    await menu_handler(message)


@router.message(F.text == "ℹ️ Yordam") 
async def reply_help_handler(message: Message):
    """Reply klaviatura yordam tugmasi"""
    await help_handler(message)


@router.message(F.text == "📊 Statistika")
async def stats_handler(message: Message):
    """Umumiy statistika"""
    db_queries = DatabaseQueries()
    
    try:
        stats = await db_queries.get_platform_statistics()
        
        stats_text = f"""
📊 <b>Platforma Statistikasi</b>

👥 <b>Foydalanuvchilar:</b>
• Jami: {stats['total_users']}
• Bugun faol: {stats['active_users_24h']}
• Yangi (hafta): {stats['new_users_week']}

🎬 <b>Kontent:</b>
• Jami kinolar: {stats['total_movies']}
• Jami ko'rishlar: {stats['total_views']}
• Faol kanallar: {stats['active_channels']}

👑 <b>Adminlar:</b> {stats['admin_count']}
"""
        
        await message.answer(stats_text, parse_mode="HTML")
        
    except Exception as e:
        await message.answer("❌ Statistika yuklashda xatolik.")
        print(f"Stats handler error: {e}")


def register_start_handlers(dp):
    """Start handlerlarni ro'yxatga olish"""
    dp.include_router(router)