from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import settings
from app.handlers import register_all_handlers
from app.middlewares import register_all_middlewares

def create_bot():
    """Bot va Dispatcher yaratish"""
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    
    # Middlewarelarni ro'yxatga olish
    register_all_middlewares(dp)
    
    # Handlerlarni ro'yxatga olish
    register_all_handlers(dp)
    
    return bot, dp