"""
Kino boshqaruvi yordamchi funksiyalar
"""

from typing import Optional
from aiogram.types import Message, InputMediaVideo
from aiogram.exceptions import TelegramBadRequest

from app.database.models import Movie, User
from app.database import DatabaseQueries
from app.keyboards.inline_keyboards import get_movie_keyboard

from app.config import settings

async def send_movie_to_user(message: Message, movie: Movie, user: User, db_queries: DatabaseQueries) -> bool:
    """
    Foydalanuvchiga kino yuborish
    
    Args:
        message: Telegram message obyekti
        movie: Kino obyekti
        user: Foydalanuvchi obyekti
        db_queries: Database queries instance
    
    Returns:
        bool: Yuborish muvaffaqiyatligi
    """
    
    try:
        # Kino caption yaratish
        caption = format_movie_caption(movie, user)
        
        # Klaviatura yaratish
        keyboard = get_movie_keyboard(movie)
        
        # Video yuborish
        await message.answer_video(
            video=movie.file_id,
            caption=caption,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        # Ko'rish statistikasini qayd etish
        await db_queries.add_movie_view(user.id, movie.id)
        
        print(f"Movie {movie.code} sent to user {user.tg_id}")
        return True
        
    except TelegramBadRequest as e:
        print(f"Failed to send movie {movie.code}: {e}")
        
        # Fallback - matn bilan yuborish
        await message.answer(
            f"❌ Kino yuklashda xatolik: {e}\n\n"
            f"🎬 <b>{movie.title}</b>\n"
            f"📝 Kod: <code>{movie.code}</code>\n\n"
            f"🔄 Iltimos, keyinroq qayta urinib ko'ring.",
            parse_mode="HTML"
        )
        return False
    
    except Exception as e:
        print(f"Unexpected error sending movie: {e}")
        await message.answer("❌ Kutilmagan xatolik yuz berdi.")
        return False


async def send_movie_to_user_from_private(message: Message, movie, user, db_queries):
    """Private channeldan message_id bo'yicha kinoni yuborish"""
    try:
        # Private channeldan xabarni ko'chirish
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=settings.private_channel_id,
            message_id=movie.private_message_id,
        )
        
        # Ko'rishlar sonini yangilash
        await db_queries.increment_movie_views(movie.id)

        # Movie view qayd etish (mavjud metod)
        await db_queries.add_movie_view(user.id, movie.id)
        
        # Foydalanuvchi faoliyatini yangilash
        await db_queries.update_user_activity(user.tg_id)

        
        # Muvaffaqiyat xabari
        await message.answer(
            "✅ Film muvaffaqiyatli yuborildi!\n\n"
            "🔄 Boshqa filmlar uchun /menu tugmasini bosing.",
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.answer(
            "❌ Filmni yuborishda xatolik yuz berdi.\n\n"
            "🔄 Iltimos, qaytadan urinib ko'ring yoki admin bilan bog'laning."
        )
        print(f"Send movie from private error: {e}")

def format_movie_caption(movie: Movie, user: User) -> str:
    """
    Kino uchun caption formatlash
    
    Args:
        movie: Kino obyekti
        user: Foydalanuvchi obyekti
    
    Returns:
        str: Formatlanган caption
    """
    
    caption = f"""
🎬 <b>{movie.title}</b>

📝 <b>Kod:</b> <code>{movie.code}</code>
👁 <b>Ko'rishlar:</b> {movie.view_count}

"""
    
    if movie.description:
        caption += f"📖 <b>Tavsif:</b>\n{movie.description}\n\n"
    
    caption += f"""
🎯 <b>Yaxshi tomosha!</b>

💡 Boshqa kinolar uchun kod yuboring yoki /menu bosing.

👤 <b>Tomoshabin:</b> {user.full_name}
"""
    
    return caption


async def check_movie_access(user_id: int, movie_code: str, db_queries: DatabaseQueries) -> dict:
    """
    Kinoga kirish huquqini tekshirish
    
    Args:
        user_id: Telegram foydalanuvchi ID
        movie_code: Kino kodi
        db_queries: Database queries instance
    
    Returns:
        dict: Kirish ma'lumotlari
    """
    
    try:
        # Foydalanuvchini topish
        user = await db_queries.get_user_by_tg_id(user_id)
        if not user:
            return {
                'allowed': False,
                'reason': 'user_not_found',
                'message': 'Foydalanuvchi topilmadi. /start bosing.'
            }
        
        # Kinoni topish
        movie = await db_queries.get_movie_by_code(movie_code)
        if not movie:
            return {
                'allowed': False,
                'reason': 'movie_not_found',
                'message': f'Kino kodi {movie_code} topilmadi.'
            }
        
        # Obuna holatini tekshirish
        subscription_info = await db_queries.check_user_subscription(user.id)
        
        if not subscription_info.is_subscribed_to_all():
            unsubscribed_channels = subscription_info.get_unjoined_channels()
            return {
                'allowed': False,
                'reason': 'not_subscribed',
                'message': "Barcha kanallarga obuna bo'ling.",
                'unsubscribed_channels': unsubscribed_channels,
                'subscription_info': subscription_info
            }
        
        # Barcha shartlar bajarilgan
        return {
            'allowed': True,
            'user': user,
            'movie': movie,
            'subscription_info': subscription_info
        }
        
    except Exception as e:
        print(f"Movie access check error: {e}")
        return {
            'allowed': False,
            'reason': 'system_error',
            'message': 'Tizim xatoligi yuz berdi.'
        }


async def get_movie_recommendations(user: User, db_queries: DatabaseQueries, limit: int = 5) -> list:
    """
    Foydalanuvchi uchun kino tavsiyalari
    
    Args:
        user: Foydalanuvchi obyekti
        db_queries: Database queries instance
        limit: Tavsiyalar soni
    
    Returns:
        list: Tavsiya qilingan kinolar ro'yxati
    """
    
    try:
        # Foydalanuvchi tomosha qilgan kinolar
        user_history = await db_queries.get_user_movie_history(user.id, limit=50)
        watched_movie_ids = [item['movie_id'] for item in user_history]
        
        # Mashhur kinolardan tavsiya
        popular_movies = await db_queries.get_popular_movies(limit=limit*2)
        
        # Tomosha qilmagan kinolarni filtrlash
        recommendations = []
        for movie in popular_movies:
            if movie.id not in watched_movie_ids:
                recommendations.append(movie)
                if len(recommendations) >= limit:
                    break
        
        # Agar kam bo'lsa, yangi kinolardan qo'shish
        if len(recommendations) < limit:
            recent_movies = await db_queries.get_recent_movies(limit=limit*2)
            for movie in recent_movies:
                if movie.id not in watched_movie_ids and movie not in recommendations:
                    recommendations.append(movie)
                    if len(recommendations) >= limit:
                        break
        
        return recommendations[:limit]
        
    except Exception as e:
        print(f"Recommendations error: {e}")
        return []


def format_movie_info(movie: Movie, include_stats: bool = False, stats: Optional[dict] = None) -> str:
    """
    Kino ma'lumotlarini formatlash
    
    Args:
        movie: Kino obyekti
        include_stats: Statistika qo'shish yoki yo'q
        stats: Statistika ma'lumotlari
    
    Returns:
        str: Formatlangan ma'lumot
    """
    
    info = f"""
🎬 <b>{movie.title}</b>

📝 <b>Kod:</b> <code>{movie.code}</code>
🆔 <b>ID:</b> {movie.id}
📅 <b>Qo'shilgan:</b> {movie.created_at.strftime('%Y-%m-%d %H:%M')}
"""
    
    if movie.description:
        info += f"\n📖 <b>Tavsif:</b>\n{movie.description}\n"
    
    if include_stats and stats:
        info += f"""
📊 <b>Statistika:</b>
• Jami ko'rishlar: {stats.get('total_views', movie.view_count)}
• Noyob tomoshabinlar: {stats.get('unique_viewers', "Noma'lum")}
• Oxirgi 24 soat: {stats.get('recent_views', "Noma'lum")}
• Mashhurlik ball: {stats.get('popularity_score', "Noma'lum")}
"""
    else:
        info += f"\n👁 <b>Ko'rishlar:</b> {movie.view_count}"
    
    info += f"\n💡 <b>Ko'rish uchun kodni yuboring:</b> <code>{movie.code}</code>"
    
    return info


async def search_movies_advanced(search_term: str, db_queries: DatabaseQueries, filters: Optional[dict] = None) -> list:
    """
    Ilg'or kino qidirish
    
    Args:
        search_term: Qidiruv so'zi
        db_queries: Database queries instance
        filters: Qo'shimcha filtrlar
    
    Returns:
        list: Topilgan kinolar
    """
    
    try:
        # Asosiy qidirish
        movies = await db_queries.search_movies(search_term, limit=50)
        
        if not filters:
            return movies[:10]
        
        # Filtrlarni qo'llash
        filtered_movies = []
        
        for movie in movies:
            # Yil filtri
            if filters.get('year') and movie.created_at.year != filters['year']:
                continue
            
            # Minimal ko'rishlar filtri
            if filters.get('min_views') and movie.view_count < filters['min_views']:
                continue
            
            # Maksimal ko'rishlar filtri
            if filters.get('max_views') and movie.view_count > filters['max_views']:
                continue
            
            filtered_movies.append(movie)
        
        return filtered_movies[:10]
        
    except Exception as e:
        print(f"Advanced search error: {e}")
        return []


async def get_movie_analytics(movie: Movie, db_queries: DatabaseQueries) -> dict:
    """
    Kino uchun batafsil analitika
    
    Args:
        movie: Kino obyekti
        db_queries: Database queries instance
    
    Returns:
        dict: Analitika ma'lumotlari
    """
    
    try:
        # Asosiy statistika
        stats = await db_queries.get_movie_stats(movie.id)
        
        # Ko'rgan foydalanuvchilar
        viewers = await db_queries.get_movie_viewers(movie.id, limit=100)
        
        # Kunlik ko'rishlar (oxirgi 7 kun)
        daily_views = {}
        for viewer in viewers:
            date = viewer['viewed_at'].date()
            daily_views[date] = daily_views.get(date, 0) + 1
        
        return {
            'basic_stats': stats.to_dict() if stats else {},
            'total_viewers': len(viewers),
            'daily_views': daily_views,
            'avg_views_per_day': sum(daily_views.values()) / max(len(daily_views), 1),
            'peak_day': max(daily_views.items(), key=lambda x: x[1]) if daily_views else None
        }
        
    except Exception as e:
        print(f"Movie analytics error: {e}")
        return {}


def validate_movie_data(title: str, code: str, description: str = "") -> dict:
    """
    Kino ma'lumotlarini validatsiya qilish
    
    Args:
        title: Kino nomi
        code: Kino kodi
        description: Tavsif
    
    Returns:
        dict: Validatsiya natijalari
    """
    
    errors = []
    
    # Nom validatsiyasi
    if not title or len(title.strip()) < 3:
        errors.append("Kino nomi kamida 3 ta belgidan iborat bo'lishi kerak")
    elif len(title.strip()) > 100:
        errors.append("Kino nomi 100 ta belgidan oshmasligi kerak")
    
    # Kod validatsiyasi
    if not code or len(code.strip()) < 3:
        errors.append("Kino kodi kamida 3 ta belgidan iborat bo'lishi kerak")
    elif len(code.strip()) > 20:
        errors.append("Kino kodi 20 ta belgidan oshmasligi kerak")
    elif not code.replace('_', '').isalnum():
        errors.append("Kino kodi faqat harf, raqam va _ belgisidan iborat bo'lishi kerak")
    
    # Tavsif validatsiyasi
    if description and len(description.strip()) > 500:
        errors.append("Tavsif 500 ta belgidan oshmasligi kerak")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'cleaned_data': {
            'title': title.strip(),
            'code': code.strip().upper(),
            'description': description.strip() if description else ""
        }
    }