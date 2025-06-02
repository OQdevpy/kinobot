import asyncio
import logging
from app.bot import create_bot
from app.database.connection import init_db

async def main():
    """Asosiy funksiya"""
    # Ma'lumotlar bazasini ishga tushirish
    await init_db()
    
    # Bot yaratish va ishga tushirish
    bot, dp = create_bot()
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())