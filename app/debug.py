async def debug_channel_access(bot):
    """Channel access ni tekshirish"""
    from app.config import settings
    
    try:
        # Channel ma'lumotlarini olishga harakat qilish
        chat_info = await bot.get_chat(settings.publish_channel_id)
        print(f"✅ Channel topildi: {chat_info.title}")
        print(f"   - ID: {chat_info.id}")
        print(f"   - Type: {chat_info.type}")
        print(f"   - Username: @{chat_info.username}" if chat_info.username else "   - Username: Yo'q")
        
        # Bot admin ekanligini tekshirish
        try:
            bot_member = await bot.get_chat_member(settings.publish_channel_id, bot.id)
            print(f"   - Bot status: {bot_member.status}")
            print(f"   - Can post: {bot_member.can_post_messages if hasattr(bot_member, 'can_post_messages') else 'Unknown'}")
        except Exception as member_error:
            print(f"❌ Bot member ma'lumotlarini olishda xatolik: {member_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Channel access xatoligi: {e}")
        print(f"   - Channel ID: {settings.publish_channel_id}")
        print(f"   - Bot ID: {bot.id}")
        
        # Tavsiyalar
        print("\n💡 Tekshirish kerak:")
        print("   1. Bot channelga admin sifatida qo'shilganmi?")
        print("   2. Channel ID to'g'rimi?")
        print("   3. Bot 'Post Messages' ruxsatiga egami?")
        
        return False

# Test uchun ishlatish
async def test_channel_access(bot):
    """Channel access ni test qilish"""
    success = await debug_channel_access(bot)
    if success:
        print("\n🎉 Channel access muvaffaqiyatli!")
    else:
        print("\n❌ Channel access muammosi mavjud!")
        
