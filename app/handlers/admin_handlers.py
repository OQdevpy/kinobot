"""
Admin handlerlari
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from app.database import DatabaseQueries
from app.debug import debug_channel_access
from app.keyboards.inline_keyboards import (
    get_admin_main_keyboard,
    get_admin_movie_keyboard,
    get_admin_channel_keyboard,
    get_admin_users_keyboard,
    get_confirmation_keyboard
)
from app.states.admin_states import AdminStates
from app.filters.admin_filter import AdminFilter
from app.utils.admin_utils import format_admin_stats, export_data_to_file
from app.config import settings

router = Router()
router.message.filter(AdminFilter())  # Barcha handlerlar uchun admin filter


@router.message(F.text == "👑 Admin Panel")
async def admin_panel_handler(message: Message):
    """Admin paneli"""
    db_queries = DatabaseQueries()
    
    try:
        # Admin dashboard ma'lumotlari
        dashboard_data = await db_queries.get_admin_dashboard_data()
        stats = dashboard_data['platform_stats']
        
        admin_text = f"""
👑 <b>Admin Panel</b>

📊 <b>Platforma Statistikasi:</b>
• Foydalanuvchilar: {stats['total_users']}
• Kinolar: {stats['total_movies']}
• Kanallar: {stats['active_channels']}
• Jami ko'rishlar: {stats['total_views']}
• Bugun faol: {stats['active_users_24h']}

🎯 <b>Nima qilmoqchisiz?</b>
"""
        
        keyboard = get_admin_main_keyboard()
        
        await message.answer(
            admin_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.answer("❌ Admin panel yuklashda xatolik.")
        print(f"Admin panel error: {e}")


@router.callback_query(F.data == "admin_panel")
async def admin_panel_handler(callback: CallbackQuery):
    """Admin paneli"""
    db_queries = DatabaseQueries()
    
    try:
        # Admin dashboard ma'lumotlari
        dashboard_data = await db_queries.get_admin_dashboard_data()
        stats = dashboard_data['platform_stats']
        
        admin_text = f"""
👑 <b>Admin Panel</b>

📊 <b>Platforma Statistikasi:</b>
• Foydalanuvchilar: {stats['total_users']}
• Kinolar: {stats['total_movies']}
• Kanallar: {stats['active_channels']}
• Jami ko'rishlar: {stats['total_views']}
• Bugun faol: {stats['active_users_24h']}

🎯 <b>Nima qilmoqchisiz?</b>
"""
        
        keyboard = get_admin_main_keyboard()

        
        await callback.message.edit_text(
            admin_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        await callback.answer()  # Callback queryni javoblash
        
    except Exception as e:
        await callback.answer("❌ Admin panel yuklashda xatolik.", show_alert=True)
        print(f"Admin panel error: {e}")

@router.callback_query(F.data == "admin_movies")
async def admin_movies_handler(callback: CallbackQuery):
    """Kinolar boshqaruvi"""
    await callback.answer()
    
    db_queries = DatabaseQueries()
    
    try:
        movies_count = await db_queries.get_movies_count()
        popular_movies = await db_queries.get_popular_movies(limit=5)
        
        movies_text = f"""
🎬 <b>Kinolar Boshqaruvi</b>

📊 <b>Statistika:</b>
• Jami kinolar: {movies_count}

🔥 <b>Top 5 mashhur:</b>
"""
        
        for i, movie in enumerate(popular_movies, 1):
            movies_text += f"{i}. {movie.title} ({movie.view_count} ko'rish)\n"
        
        keyboard = get_admin_movie_keyboard()
        
        await callback.message.edit_text(
            movies_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.message.edit_text("❌ Kinolar ma'lumotini yuklashda xatolik.")
        print(f"Admin movies error: {e}")



@router.callback_query(F.data == "add_movie")
async def add_movie_request_handler(callback: CallbackQuery, state: FSMContext):
    """Yangi kino qo'shish so'rovi"""
    await callback.answer()
    await state.set_state(AdminStates.waiting_movie_video)
    
    add_movie_text = """
➕ <b>Yangi Kino Qo'shish</b>

📹 <b>1-qadam:</b> Video faylni yuboring

⚠️ <b>Talablar:</b>
• Video fayl bo'lishi shart
• Maksimal hajm: 50MB (Telegram limit)
• MP4 formatida bo'lsa yaxshi

❌ Bekor qilish uchun /cancel yozing
"""
    
    await callback.message.edit_text(add_movie_text, parse_mode="HTML")


@router.message(AdminStates.waiting_movie_video, F.content_type == ContentType.VIDEO)
async def add_movie_video_handler(message: Message, state: FSMContext):
    """Video fayl qabul qilish"""
    
    try:
        await state.update_data(
            file_id=message.video.file_id,
        )
        await state.set_state(AdminStates.waiting_movie_private_message_id)
        
        link_text = """
🔗 <b>2-qadam:</b> Kino havolasini yozing

💡 <b>Misol:</b> https://t.me/private_channel/123

⚠️ <b>Talablar:</b>
• To'liq havola bo'lishi shart
• Private kanaldagi xabar havolasi

❌ Bekor qilish uchun /cancel yozing
"""
        
        await message.answer(link_text, parse_mode="HTML")
        
    except Exception as e:
        await message.answer(f"❌ Video private channelga yuklashda xatolik: {str(e)}")
        print(f"Forward video error: {e}")


@router.message(AdminStates.waiting_movie_private_message_id)
async def add_private_message_id_handler(message: Message, state: FSMContext):
    """Kino havolasini qabul qilish"""
    
    link = message.text.strip()
    
    # Link validatsiyasi
    if not link.startswith("https://t.me/"):
        await message.answer("❌ Havola https://t.me/ bilan boshlanishi kerak.")
        return
    
    # Linkni saqlash
    await state.update_data(private_message_id=link.split('/')[-1])
    await state.set_state(AdminStates.waiting_movie_code)
    
    code_text = """
📝 <b>3-qadam:</b> Kino kodini yozing

💡 <b>Misol:</b> MOVIE001, ACTION123, DRAMA456

⚠️ <b>Qoidalar:</b>
• Faqat harf va raqamlar
• Minimal 3 ta belgi
• Maksimal 20 ta belgi
• Noyob bo'lishi shart

❌ Bekor qilish uchun /cancel yozing
"""
    
    await message.answer(code_text, parse_mode="HTML")


@router.message(AdminStates.waiting_movie_code)
async def add_movie_code_handler(message: Message, state: FSMContext):
    """Kino kodini qabul qilish"""
    
    code = message.text.strip().upper()
    
    # Kod validatsiyasi
    if len(code) < 3 or len(code) > 20:
        await message.answer("❌ Kod 3-20 ta belgi orasida bo'lishi kerak.")
        return
    
    if not code.replace('_', '').isalnum():
        await message.answer("❌ Kod faqat harf, raqam va _ belgisidan iborat bo'lishi kerak.")
        return
    
    # Kod noyobligini tekshirish
    db_queries = DatabaseQueries()
    existing_movie = await db_queries.get_movie_by_code(code)
    
    if existing_movie:
        await message.answer(f"❌ <code>{code}</code> kodi allaqachon mavjud. Boshqa kod tanlang.")
        return
    
    # Kodni saqlash
    await state.update_data(code=code)
    await state.set_state(AdminStates.waiting_movie_title)
    
    title_text = """
🎬 <b>4-qadam:</b> Kino nomini yozing

💡 <b>Misol:</b> Spider-Man: No Way Home

⚠️ <b>Qoidalar:</b>
• Minimal 3 ta belgi
• Maksimal 100 ta belgi

❌ Bekor qilish uchun /cancel yozing
"""
    
    await message.answer(title_text, parse_mode="HTML")


@router.message(AdminStates.waiting_movie_title)
async def add_movie_title_handler(message: Message, state: FSMContext):
    """Kino nomini qabul qilish"""
    
    title = message.text.strip()
    
    if len(title) < 3 or len(title) > 100:
        await message.answer("❌ Kino nomi 3-100 ta belgi orasida bo'lishi kerak.")
        return
    
    await state.update_data(title=title)
    await state.set_state(AdminStates.waiting_movie_description)
    
    description_text = """
📖 <b>5-qadam:</b> Kino tavsifini yozing

💡 <b>Misol:</b> Spider-Man jamoaviy koinoti haqidagi ajoyib film...

⚠️ <b>Qoidalar:</b>
• Maksimal 500 ta belgi
• Ixtiyoriy (bo'sh qoldirish mumkin)

❌ Bekor qilish uchun /cancel yozing
⏩ O'tkazib yuborish uchun /skip yozing
"""
    
    await message.answer(description_text, parse_mode="HTML")


@router.message(AdminStates.waiting_movie_description)
async def add_movie_description_handler(message: Message, state: FSMContext):
    """Kino tavsifini qabul qilish"""
    
    description = ""
    
    if message.text.strip() != "/skip":
        description = message.text.strip()
        
        if len(description) > 500:
            await message.answer("❌ Tavsif 500 ta belgidan oshmasligi kerak.")
            return
    
    # Barcha ma'lumotlarni olish
    data = await state.get_data()
    
    # Tasdiqlash xabari
    confirmation_text = f"""
✅ <b>Kino Ma'lumotlarini Tasdiqlang</b>

🎬 <b>Nom:</b> {data['title']}
📝 <b>Kod:</b> <code>{data['code']}</code>
🔗 <b>Havola:</b> https://t.me/c/{str(settings.private_channel_id)[3:]}/{data['private_message_id']}
📖 <b>Tavsif:</b> {description or "Tavsif yo'q"}

🎯 <b>Kinoni qo'shamizmi va publish qilamizmi?</b>
"""
    
    # Ma'lumotlarni saqlash
    await state.update_data(description=description)
    
    keyboard = get_confirmation_keyboard("confirm_add_movie", "cancel_add_movie")
    
    await message.answer(
        confirmation_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "confirm_add_movie")
async def confirm_add_movie_handler(callback: CallbackQuery, state: FSMContext):
        """Kino qo'shishni tasdiqlash va publish qilish"""
        await callback.answer()
    
    # try:
        data = await state.get_data()
        db_queries = DatabaseQueries()
        
        # Kinoni ma'lumotlar bazasiga qo'shish
        movie = await db_queries.create_movie(
            file_id=data['file_id'],
            code=data['code'],
            title=data['title'],
            description=data['description'],
            private_message_id=int(data['private_message_id'])  # Yangi maydon
        )
        
        # Public channelga post qilish
        await publish_movie_to_channel(callback.bot, movie)
        
        await state.clear()
        
        success_text = f"""
✅ <b>Kino muvaffaqiyatli qo'shildi va publish qilindi!</b>

🎬 <b>Nom:</b> {movie.title}
📝 <b>Kod:</b> <code>{movie.code}</code>
🆔 <b>ID:</b> {movie.id}
📺 <b>Channel:</b> Kino public channelga joylandi

🎯 Endi foydalanuvchilar <code>{movie.code}</code> kodini yuborib kinoni tomosha qila olishadi!
"""
        
        await callback.message.edit_text(success_text, parse_mode="HTML")
        
    # except Exception as e:
    #     await callback.message.edit_text(f"❌ Kino qo'shishda xatolik: {str(e)}")
    #     await state.clear()
    #     print(f"Add movie error: {e}")


async def publish_movie_to_channel(bot, movie):
    """Kinoni public channelga publish qilish"""
    
    try:
        # Bot username olish
        bot_info = await bot.get_me()
        bot_username = bot_info.username
        
        # Short video (thumb) yaratish uchun video ma'lumotlarini olish
        # Bu yerda video dan screenshot olish yoki mavjud thumb ishlatish mumkin
        
        # Public channel uchun post matni
        post_text = f"""
🎬 <b>{movie.title}</b>

📖 {movie.description or "Ajoyib kino sizni kutmoqda!"}

🎯 <b>Ko'rish uchun:</b>
👇 Pastdagi tugmani bosing yoki botga <code>{movie.code}</code> kodini yuboring

🤖 @{bot_username}
"""
        
        # Inline keyboard yaratish
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🎬 Kinoni Ko'rish",
                url=f"https://t.me/{bot_username}?start={movie.code}"
            )],
            [InlineKeyboardButton(
                text="🤖 Botga O'tish",
                url=f"https://t.me/{bot_username}"
            )]
        ])
        
        # Agar video fayl hajmi kichik bo'lsa, to'g'ridan-to'g'ri yuborish
        # Aks holda, faqat matn va tugma yuborish
        try:
            # Video bilan post
            await debug_channel_access(bot)
            await bot.send_video(
                chat_id=settings.publish_channel_id,
                video=movie.file_id,
                caption=post_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as video_error:
            print(f"Video yuborish xatoligi: {video_error}")
            # Agar video yuborib bo'lmasa, faqat matn yuborish
            await bot.send_message(
                chat_id=settings.publish_channel_id,
                text=post_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        
        print(f"Movie {movie.code} published to channel {settings.publish_channel_id}")
        
    except Exception as e:
        print(f"Publish to channel error: {e}")
        raise


@router.callback_query(F.data == "cancel_add_movie")
async def cancel_add_movie_handler(callback: CallbackQuery, state: FSMContext):
    """Kino qo'shishni bekor qilish"""
    await callback.answer()
    
    try:
        # Agar private channelga forward qilingan bo'lsa, uni o'chirish
        data = await state.get_data()
        if 'private_message_id' in data:
            try:
                await callback.bot.delete_message(
                    chat_id=settings.private_channel_id,
                    message_id=data['private_message_id']
                )
            except Exception as e:
                print(f"Delete forwarded message error: {e}")
        
        await state.clear()
        await callback.message.edit_text("❌ Kino qo'shish bekor qilindi.")
        
    except Exception as e:
        await state.clear()
        await callback.message.edit_text("❌ Kino qo'shish bekor qilindi.")
        print(f"Cancel movie error: {e}")


@router.callback_query(F.data == "admin_channels")
async def admin_channels_handler(callback: CallbackQuery):
    """Kanallar boshqaruvi"""
    await callback.answer()
    
    db_queries = DatabaseQueries()
    
    try:
        channels = await db_queries.get_all_channels()
        active_channels = [ch for ch in channels if ch.is_active()]
        
        channels_text = f"""
📺 <b>Kanallar Boshqaruvi</b>

📊 <b>Statistika:</b>
• Jami kanallar: {len(channels)}
• Faol kanallar: {len(active_channels)}

📋 <b>Kanallar ro'yxati:</b>
"""
        
        for channel in channels[:10]:  # Faqat birinchi 10 tasini ko'rsatish
            status_icon = "🟢" if channel.is_active() else "🔴"
            subscribers_count = await db_queries.get_channel_subscribers_count(channel.id)
            
            channels_text += f"{status_icon} <b>{channel.title}</b>\n"
            channels_text += f"   👥 Obunachi: {subscribers_count}\n"
            channels_text += f"   🔗 {channel.channel_username}\n\n"
        
        keyboard = get_admin_channel_keyboard()
        
        await callback.message.edit_text(
            channels_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.message.edit_text("❌ Kanallar ma'lumotini yuklashda xatolik.")
        print(f"Admin channels error: {e}")


@router.callback_query(F.data == "add_channel")
async def add_channel_request_handler(callback: CallbackQuery, state: FSMContext):
    """Yangi kanal qo'shish so'rovi"""
    await callback.answer()
    await state.set_state(AdminStates.waiting_channel_title)
    
    add_channel_text = """
➕ <b>Yangi Kanal Qo'shish</b>

📝 <b>1-qadam:</b> Kanal nomini yozing

💡 <b>Misol:</b> Kinematika Rasmiy Kanali

⚠️ <b>Talablar:</b>
• Minimal 3 ta belgi
• Maksimal 50 ta belgi

❌ Bekor qilish uchun /cancel yozing
"""
    
    await callback.message.edit_text(add_channel_text, parse_mode="HTML")


@router.message(AdminStates.waiting_channel_title)
async def add_channel_title_handler(message: Message, state: FSMContext):
    """Kanal nomini qabul qilish"""
    
    title = message.text.strip()
    
    if len(title) < 3 or len(title) > 50:
        await message.answer("❌ Kanal nomi 3-50 ta belgi orasida bo'lishi kerak.")
        return
    
    await state.update_data(title=title)
    await state.set_state(AdminStates.waiting_channel_link)
    
    link_text = """
🔗 <b>2-qadam:</b> Kanal havolasini yozing

💡 <b>Misol:</b> https://t.me/kinematika_official

⚠️ <b>Talablar:</b>
• To'liq havola bo'lishi shart
• https://t.me/ bilan boshlanishi kerak

❌ Bekor qilish uchun /cancel yozing
"""
    
    await message.answer(link_text, parse_mode="HTML")


@router.message(AdminStates.waiting_channel_link)
async def add_channel_link_handler(message: Message, state: FSMContext):
    """Kanal havolasini qabul qilish"""
    
    link = message.text.strip()
    
    if not link.startswith("https://t.me/"):
        await message.answer("❌ Havola https://t.me/ bilan boshlanishi kerak.")
        return
    
    # Username ni ajratib olish
    username = link.split("/")[-1]
    if not username.startswith("@"):
        username = "@" + username
    
    await state.update_data(link=link, username=username)
    await state.set_state(AdminStates.waiting_channel_status)
    
    status_text = """
⚙️ <b>3-qadam:</b> Kanal holatini tanlang

📋 <b>Variantlar:</b>
• aktiv - Kanal majburiy obuna ro'yxatida
• noaktiv - Kanal o'chirilgan

💡 <b>Yozing:</b> aktiv yoki noaktiv

❌ Bekor qilish uchun /cancel yozing
"""
    
    await message.answer(status_text, parse_mode="HTML")


@router.message(AdminStates.waiting_channel_status)
async def add_channel_status_handler(message: Message, state: FSMContext):
    """Kanal holatini qabul qilish"""
    
    status = message.text.strip().lower()
    
    if status not in ["aktiv", "noaktiv"]:
        await message.answer("❌ Faqat 'aktiv' yoki 'noaktiv' yozing.")
        return
    
    # Barcha ma'lumotlarni olish
    data = await state.get_data()
    
    # Tasdiqlash xabari
    confirmation_text = f"""
✅ <b>Kanal Ma'lumotlarini Tasdiqlang</b>

📝 <b>Nom:</b> {data['title']}
🔗 <b>Havola:</b> {data['link']}
👤 <b>Username:</b> {data['username']}
⚙️ <b>Holat:</b> {status}

🎯 <b>Kanalni qo'shamizmi?</b>
"""
    
    await state.update_data(status=status)
    
    keyboard = get_confirmation_keyboard("confirm_add_channel", "cancel_add_channel")
    
    await message.answer(
        confirmation_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "confirm_add_channel")
async def confirm_add_channel_handler(callback: CallbackQuery, state: FSMContext):
    """Kanal qo'shishni tasdiqlash"""
    await callback.answer()
    
    try:
        data = await state.get_data()
        db_queries = DatabaseQueries()
        
        # Kanalni ma'lumotlar bazasiga qo'shish
        channel = await db_queries.create_channel(
            title=data['title'],
            channel_link=data['link'],
            channel_username=data['username'],
            status=data['status']
        )
        
        await state.clear()
        
        success_text = f"""
✅ <b>Kanal muvaffaqiyatli qo'shildi!</b>

📝 <b>Nom:</b> {channel.title}
🔗 <b>Havola:</b> {channel.channel_link}
👤 <b>Username:</b> {channel.channel_username}
⚙️ <b>Holat:</b> {channel.status}

🎯 Endi bu kanal majburiy obuna ro'yxatida!
"""
        
        await callback.message.edit_text(success_text, parse_mode="HTML")
        
    except Exception as e:
        await callback.message.edit_text(f"❌ Kanal qo'shishda xatolik: {str(e)}")
        await state.clear()
        print(f"Add channel error: {e}")


@router.callback_query(F.data == "cancel_add_channel")
async def cancel_add_channel_handler(callback: CallbackQuery, state: FSMContext):
    """Kanal qo'shishni bekor qilish"""
    await callback.answer()
    await state.clear()
    
    await callback.message.edit_text("❌ Kanal qo'shish bekor qilindi.")


@router.callback_query(F.data == "admin_users")
async def admin_users_handler(callback: CallbackQuery):
    """Foydalanuvchilar boshqaruvi"""
    await callback.answer()
    
    db_queries = DatabaseQueries()
    
    try:
        stats = await db_queries.get_platform_statistics()
        active_users = await db_queries.get_active_users(days=7, limit=5)
        
        users_text = f"""
👥 <b>Foydalanuvchilar Boshqaruvi</b>

📊 <b>Statistika:</b>
• Jami foydalanuvchilar: {stats['total_users']}
• Bugun faol: {stats['active_users_24h']}
• Yangi (hafta): {stats['new_users_week']}
• Adminlar: {stats['admin_count']}

🔥 <b>Eng faol foydalanuvchilar (hafta):</b>
"""
        
        for user_data in active_users:
            users_text += f"• {user_data['full_name']} ({user_data['movies_watched']} kino)\n"
        
        keyboard = get_admin_users_keyboard()
        
        await callback.message.edit_text(
            users_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.message.edit_text("❌ Foydalanuvchilar ma'lumotini yuklashda xatolik.")
        print(f"Admin users error: {e}")


@router.callback_query(F.data == "admin_statistics")
async def admin_statistics_handler(callback: CallbackQuery):
    """Batafsil statistika"""
    await callback.answer()
    
    db_queries = DatabaseQueries()
    
    try:
        dashboard_data = await db_queries.get_admin_dashboard_data()
        stats = format_admin_stats(dashboard_data)
        
        await callback.message.edit_text(
            stats,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.message.edit_text("❌ Statistika yuklashda xatolik.")
        print(f"Admin statistics error: {e}")


@router.callback_query(F.data == "export_data")
async def export_data_handler(callback: CallbackQuery):
    """Ma'lumotlarni eksport qilish"""
    await callback.answer("📊 Ma'lumotlar tayyorlanmoqda...")
    
    try:
        db_queries = DatabaseQueries()
        backup_data = await db_queries.backup_data()
        
        # Faylga saqlash
        file_path = await export_data_to_file(backup_data)
        
        # Faylni yuborish
        with open(file_path, 'rb') as file:
            await callback.message.answer_document(
                file,
                caption=f"📊 <b>Ma'lumotlar eksporti</b>\n\n"
                        f"📅 Sana: {backup_data['backup_date']}\n"
                        f"📋 Jami yozuvlar: {backup_data['total_records']}",
                parse_mode="HTML"
            )
        
        # Vaqtinchalik faylni o'chirish
        import os
        os.remove(file_path)
        
    except Exception as e:
        await callback.message.answer("❌ Eksport qilishda xatolik.")
        print(f"Export error: {e}")


@router.message(Command("cancel"), AdminStates())
async def cancel_admin_action_handler(message: Message, state: FSMContext):
    """Admin amallarini bekor qilish"""
    await state.clear()
    await message.answer("❌ Amal bekor qilindi.")


@router.message(Command("skip"), AdminStates.waiting_movie_description)
async def skip_description_handler(message: Message, state: FSMContext):
    """Tavsifni o'tkazib yuborish"""
    await add_movie_description_handler(message, state)


def register_admin_handlers(dp):
    """Admin handlerlarni ro'yxatga olish"""
    dp.include_router(router)