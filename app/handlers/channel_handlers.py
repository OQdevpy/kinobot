"""
Kanal tekshirish handlerlari
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter

from app.database import DatabaseQueries
from app.keyboards.inline_keyboards import get_subscription_keyboard, get_channels_list_keyboard
from app.utils.channel_checker import check_user_channel_subscription, get_unsubscribed_channels_text

router = Router()


@router.message(F.text == "📺 Kanallar")
async def channels_list_handler(message: Message):
    """Majburiy kanallar ro'yxati"""
    db_queries = DatabaseQueries()
    
    try:
        # Barcha faol kanallarni olish
        active_channels = await db_queries.get_active_channels()
        
        if not active_channels:
            await message.answer(
                "📺 <b>Majburiy Kanallar</b>\n\n"
                "❌ Hozircha majburiy kanallar yo'q.",
                parse_mode="HTML"
            )
            return
        
        # Foydalanuvchi obuna holatini tekshirish
        user = await db_queries.get_user_by_tg_id(message.from_user.id)
        subscription_info = await db_queries.check_user_subscription(user.id) if user else None
        
        channels_text = "📺 <b>Majburiy Kanallar Ro'yxati</b>\n\n"
        
        for i, channel in enumerate(active_channels, 1):
            # Obuna holatini tekshirish
            is_subscribed = False
            if subscription_info:
                is_subscribed = channel.id in subscription_info.joined_channels
            
            status_icon = "✅" if is_subscribed else "❌"
            subscribers_count = await db_queries.get_channel_subscribers_count(channel.id)
            
            channels_text += f"{i}. {status_icon} <b>{channel.title}</b>\n"
            channels_text += f"   👥 Obunachi: {subscribers_count}\n"
            channels_text += f"   🔗 {channel.channel_link}\n\n"
        
        if subscription_info and subscription_info.is_subscribed_to_all():
            channels_text += "🎉 <b>Siz barcha kanallarga obuna bo'lgansiz!</b>"
        else:
            channels_text += "⚠️ <b>Kinolarni ko'rish uchun barcha kanallarga obuna bo'ling!</b>"
        
        keyboard = get_channels_list_keyboard(active_channels)
        
        await message.answer(
            channels_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.answer("❌ Kanallar ro'yxatini yuklashda xatolik.")
        print(f"Channels list error: {e}")


@router.callback_query(F.data.startswith("join_channel:"))
async def join_channel_handler(callback: CallbackQuery):
    """Kanalga obuna bo'lish tugmasi"""
    await callback.answer()
    
    try:
        channel_id = int(callback.data.split(":")[1])
        
        db_queries = DatabaseQueries()
        channel = await db_queries.get_channel_by_id(channel_id)
        
        if not channel:
            await callback.answer("❌ Kanal topilmadi.", show_alert=True)
            return
        
        join_text = f"""
📺 <b>{channel.title}</b>

🔗 <b>Kanal:</b> {channel.channel_link}

💡 <b>Qo'llanma:</b>
1. Yuqoridagi havola orqali kanalga kiring
2. "OBUNA BO'LISH" tugmasini bosing
3. Bu yerga qaytib, "✅ Obuna bo'ldim" tugmasini bosing

⚠️ <b>Diqqat:</b> Obuna bo'lmasangiz, kinolarni tomosha qila olmaysiz!
"""
        
        # Inline tugma yaratish
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📺 Kanalga o'tish",
                url=channel.channel_link
            )],
            [InlineKeyboardButton(
                text="✅ Obuna bo'ldim",
                callback_data=f"verify_subscription:{channel_id}"
            )],
            [InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data="back_to_channels"
            )]
        ])
        
        await callback.message.edit_text(
            join_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)
        print(f"Join channel error: {e}")


@router.callback_query(F.data.startswith("verify_subscription:"))
async def verify_subscription_handler(callback: CallbackQuery):
    """Obuna holatini tekshirish"""
    await callback.answer("🔄 Obuna holati tekshirilmoqda...")
    
    try:
        channel_id = int(callback.data.split(":")[1])
        
        db_queries = DatabaseQueries()
        
        # Foydalanuvchini topish
        user = await db_queries.get_user_by_tg_id(callback.from_user.id)
        if not user:
            await callback.answer("❌ Foydalanuvchi topilmadi.", show_alert=True)
            return
        
        # Kanalni topish
        channel = await db_queries.get_channel_by_id(channel_id)
        if not channel:
            await callback.answer("❌ Kanal topilmadi.", show_alert=True)
            return
        
        # Telegram API orqali obuna holatini tekshirish
        is_subscribed = await check_user_channel_subscription(
            callback.bot,
            callback.from_user.id,
            channel.channel_id
        )
        
        if is_subscribed:
            # Ma'lumotlar bazasiga qo'shish
            await db_queries.add_user_to_channel(user.id, channel_id)
            
            # Barcha kanallarga obuna bo'lganligini tekshirish
            subscription_info = await db_queries.check_user_subscription(user.id)
            
            if subscription_info.is_subscribed_to_all():
                success_text = f"""
✅ <b>Ajoyib!</b>

Siz <b>{channel.title}</b> kanaliga muvaffaqiyatli obuna bo'ldingiz!

🎉 <b>Barcha majburiy kanallarga obuna bo'lgansiz!</b>
Endi kinolarni to'liq tomosha qilishingiz mumkin.

🎬 Kino kodini yuboring yoki qidirish funksiyasidan foydalaning.
"""
            else:
                unsubscribed_channels = subscription_info.get_unjoined_channels()
                success_text = f"""
✅ <b>{channel.title}</b> kanaliga obuna bo'ldingiz!

⚠️ <b>Qolgan kanallar:</b>
"""
                for ch in unsubscribed_channels:
                    success_text += f"• {ch.title}\n"
                
                success_text += "\nBarcha kanallarga obuna bo'lgach, kinolarni tomosha qila olasiz!"
                
                # Qolgan kanallar uchun klaviatura
                keyboard = get_subscription_keyboard(unsubscribed_channels)
                
                await callback.message.edit_text(
                    success_text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                return
            
            await callback.message.edit_text(success_text, parse_mode="HTML")
            
        else:
            # Obuna bo'lmagan
            error_text = f"""
❌ <b>Obuna topilmadi</b>

Siz hali <b>{channel.title}</b> kanaliga obuna bo'lmagansiz.

💡 <b>Qayta urinish:</b>
1. Kanalga obuna bo'ling
2. Bir necha soniya kuting
3. "✅ Obuna bo'ldim" tugmasini qayta bosing

⚠️ <b>Diqqat:</b> Ba'zan Telegram obuna holatini yangilashda biroz vaqt ketadi.
"""
            
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="📺 Kanalga o'tish",
                    url=channel.channel_link
                )],
                [InlineKeyboardButton(
                    text="🔄 Qayta tekshirish",
                    callback_data=f"verify_subscription:{channel_id}"
                )],
                [InlineKeyboardButton(
                    text="🔙 Orqaga",
                    callback_data="back_to_channels"
                )]
            ])
            
            await callback.message.edit_text(
                error_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        
    except Exception as e:
        await callback.answer("❌ Tekshirishda xatolik.", show_alert=True)
        print(f"Verify subscription error: {e}")


@router.callback_query(F.data == "back_to_channels")
async def back_to_channels_handler(callback: CallbackQuery):
    """Kanallar ro'yxatiga qaytish"""
    await callback.answer()
    
    # Kanallar ro'yxatini qayta yuklash
    await channels_list_handler(callback.message)


@router.callback_query(F.data == "join_all_channels")
async def join_all_channels_handler(callback: CallbackQuery):
    """Barcha kanallarga obuna bo'lish"""
    await callback.answer()
    
    db_queries = DatabaseQueries()
    
    try:
        user = await db_queries.get_user_by_tg_id(callback.from_user.id)
        if not user:
            await callback.answer("❌ Foydalanuvchi topilmadi.", show_alert=True)
            return
        
        subscription_info = await db_queries.check_user_subscription(user.id)
        unsubscribed_channels = subscription_info.get_unjoined_channels()
        
        if not unsubscribed_channels:
            await callback.answer("✅ Siz allaqachon barcha kanallarga obuna bo'lgansiz!", show_alert=True)
            return
        
        join_all_text = """
📺 <b>Barcha Kanallarga Obuna Bo'lish</b>

⚠️ <b>Qo'llanma:</b>
1. Quyidagi har bir kanalga alohida kiring
2. "OBUNA BO'LISH" tugmasini bosing
3. Barcha kanallarga obuna bo'lgach, "✅ Hammasini tekshirish" tugmasini bosing

📋 <b>Obuna bo'lish kerak bo'lgan kanallar:</b>

"""
        
        for i, channel in enumerate(unsubscribed_channels, 1):
            join_all_text += f"{i}. <a href='{channel.channel_link}'>{channel.title}</a>\n"
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        # Har bir kanal uchun tugma yaratish
        keyboard_buttons = []
        for channel in unsubscribed_channels[:5]:  # Maksimal 5 ta tugma
            keyboard_buttons.append([InlineKeyboardButton(
                text=f"📺 {channel.title}",
                url=channel.channel_link
            )])
        
        # Tekshirish tugmasi
        keyboard_buttons.append([InlineKeyboardButton(
            text="✅ Hammasini tekshirish",
            callback_data="verify_all_subscriptions"
        )])
        
        keyboard_buttons.append([InlineKeyboardButton(
            text="🔙 Orqaga",
            callback_data="back_to_channels"
        )])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.message.edit_text(
            join_all_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.answer("❌ Xatolik yuz berdi.", show_alert=True)
        print(f"Join all channels error: {e}")


@router.callback_query(F.data == "verify_all_subscriptions")
async def verify_all_subscriptions_handler(callback: CallbackQuery):
    """Barcha obunalarni tekshirish"""
    await callback.answer("🔄 Barcha obunalar tekshirilmoqda...")
    
    try:
        db_queries = DatabaseQueries()
        user = await db_queries.get_user_by_tg_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Foydalanuvchi topilmadi.", show_alert=True)
            return
        
        # Hozirgi obuna holatini olish
        subscription_info = await db_queries.check_user_subscription(user.id)
        unsubscribed_channels = subscription_info.get_unjoined_channels()
        
        verified_channels = []
        still_unsubscribed = []
        
        # Har bir kanalga obuna holatini tekshirish
        for channel in unsubscribed_channels:
            is_subscribed = await check_user_channel_subscription(
                callback.bot,
                callback.from_user.id,
                channel.get_username_clean()
            )
            
            if is_subscribed:
                # Ma'lumotlar bazasiga qo'shish
                await db_queries.add_user_to_channel(user.id, channel.id)
                verified_channels.append(channel)
            else:
                still_unsubscribed.append(channel)
        
        # Natijani ko'rsatish
        if not still_unsubscribed:
            # Barcha kanallarga obuna bo'lgan
            success_text = """
🎉 <b>Ajoyib!</b>

✅ Siz barcha majburiy kanallarga muvaffaqiyatli obuna bo'ldingiz!

🎬 Endi kinolarni to'liq tomosha qilishingiz mumkin.

💡 Kino kodini yuboring yoki qidirish funksiyasidan foydalaning.
"""
            await callback.message.edit_text(success_text, parse_mode="HTML")
            
        else:
            # Ba'zi kanallarga obuna bo'lmagan
            partial_text = f"""
✅ <b>Obuna bo'ldi:</b> {len(verified_channels)} ta kanal

❌ <b>Qolgan kanallar:</b> {len(still_unsubscribed)} ta

📋 <b>Hali obuna bo'lmagansiz:</b>
"""
            for channel in still_unsubscribed:
                partial_text += f"• {channel.title}\n"
            
            partial_text += "\n💡 Qolgan kanallarga ham obuna bo'ling va qayta tekshiring."
            
            keyboard = get_subscription_keyboard(still_unsubscribed)
            
            await callback.message.edit_text(
                partial_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        
    except Exception as e:
        await callback.answer("❌ Tekshirishda xatolik.", show_alert=True)
        print(f"Verify all subscriptions error: {e}")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=True))
async def user_blocked_bot_handler(event: ChatMemberUpdated):
    """Foydalanuvchi botni bloklagan/blokdan chiqargan"""
    
    db_queries = DatabaseQueries()
    
    try:
        user = await db_queries.get_user_by_tg_id(event.from_user.id)
        if not user:
            return
        
        # Faoliyatni yangilash
        await db_queries.update_user_activity(event.from_user.id)
        
        # Log qilish
        if event.new_chat_member.status == "kicked":
            print(f"User {event.from_user.id} blocked the bot")
        elif event.new_chat_member.status == "member":
            print(f"User {event.from_user.id} unblocked the bot")
        
    except Exception as e:
        print(f"User chat member update error: {e}")


def register_channel_handlers(dp):
    """Channel handlerlarni ro'yxatga olish"""
    dp.include_router(router)