"""
Foydalanuvchi handlerlari
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.database import DatabaseQueries
from app.keyboards.inline_keyboards import (
    get_movie_search_keyboard, 
    get_pagination_keyboard,
    get_movie_detail_keyboard
)
from app.states.user_states import UserStates
from app.filters.channel_filter import ChannelSubscriptionFilter

router = Router()


@router.message(F.text == "🔍 Qidirish")
async def search_request_handler(message: Message, state: FSMContext):
    """Qidirish so'rovi"""
    await state.set_state(UserStates.waiting_search_query)
    
    search_text = """
🔍 <b>Kino Qidirish</b>

Qidirmoqchi bo'lgan kino nomini yozing:
"""
    
    await message.answer(search_text, parse_mode="HTML")


@router.message(UserStates.waiting_search_query)
async def search_movies_handler(message: Message, state: FSMContext):
    """Kinolarni qidirish"""
    await state.clear()
    
    search_query = message.text.strip()
    
    if len(search_query) < 2:
        await message.answer("❌ Qidiruv so'zi kamida 2 ta belgidan iborat bo'lishi kerak.")
        return
    
    db_queries = DatabaseQueries()
    
    try:
        # Kinolarni qidirish
        movies = await db_queries.search_movies(search_query, limit=10)
        
        if not movies:
            await message.answer(
                f"❌ <b>'{search_query}'</b> bo'yicha kinolar topilmadi.\n\n"
                "💡 Boshqa kalit so'zlar bilan urinib ko'ring.",
                parse_mode="HTML"
            )
            return
        
        # Natijalarni ko'rsatish
        results_text = f"🔍 <b>'{search_query}' uchun natijalar:</b>\n\n"
        
        for i, movie in enumerate(movies, 1):
            results_text += f"{i}. <b>{movie.title}</b>\n"
            results_text += f"   📝 Kod: <code>{movie.code}</code>\n"
            results_text += f"   👁 Ko'rishlar: {movie.view_count}\n\n"
        
        keyboard = get_movie_search_keyboard(movies)
        
        await message.answer(
            results_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.answer("❌ Qidirish jarayonida xatolik yuz berdi.")
        print(f"Search error: {e}")


@router.message(F.text == "📊 Mashhur kinolar")
async def popular_movies_handler(message: Message):
    """Mashhur kinolar ro'yxati"""
    db_queries = DatabaseQueries()
    
    try:
        movies = await db_queries.get_popular_movies(limit=10)
        
        if not movies:
            await message.answer("❌ Hozircha kinolar mavjud emas.")
            return
        
        popular_text = "📊 <b>Eng mashhur kinolar:</b>\n\n"
        
        for i, movie in enumerate(movies, 1):
            popular_text += f"{i}. <b>{movie.title}</b>\n"
            popular_text += f"   📝 Kod: <code>{movie.code}</code>\n"
            popular_text += f"   👁 Ko'rishlar: {movie.view_count}\n\n"
        
        keyboard = get_movie_search_keyboard(movies)
        
        await message.answer(
            popular_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.answer("❌ Mashhur kinolar yuklashda xatolik.")
        print(f"Popular movies error: {e}")


@router.message(F.text == "🆕 Yangi kinolar")
async def recent_movies_handler(message: Message):
    """Yangi kinolar ro'yxati"""
    db_queries = DatabaseQueries()
    
    try:
        movies = await db_queries.get_recent_movies(limit=10)
        
        if not movies:
            await message.answer("❌ Hozircha kinolar mavjud emas.")
            return
        
        recent_text = "🆕 <b>Yangi qo'shilgan kinolar:</b>\n\n"
        
        for i, movie in enumerate(movies, 1):
            recent_text += f"{i}. <b>{movie.title}</b>\n"
            recent_text += f"   📝 Kod: <code>{movie.code}</code>\n"
            recent_text += f"   📅 Qo'shilgan: {movie.created_at.strftime('%Y-%m-%d')}\n\n"
        
        keyboard = get_movie_search_keyboard(movies)
        
        await message.answer(
            recent_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.answer("❌ Yangi kinolar yuklashda xatolik.")
        print(f"Recent movies error: {e}")


@router.callback_query(F.data.startswith("movie_detail:"))
async def movie_detail_handler(callback: CallbackQuery):
    """Kino tafsilotlari"""
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
        
        detail_text = f"""
🎬 <b>{movie.title}</b>

📝 <b>Kod:</b> <code>{movie.code}</code>
📖 <b>Tavsif:</b> {movie.description or 'Tavsif mavjud emas'}

📊 <b>Statistika:</b>
• Ko'rishlar: {stats.total_views if stats else movie.view_count}
• Noyob tomoshabinlar: {stats.unique_viewers if stats else "Noma'lum"}
• Oxirgi 24 soat: {stats.recent_views if stats else "Noma'lum"}

💡 <b>Ko'rish uchun kodni yuboring:</b> <code>{movie.code}</code>
"""
        
        keyboard = get_movie_detail_keyboard(movie)
        
        await callback.message.edit_text(
            detail_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.message.edit_text("❌ Kino ma'lumotlarini yuklashda xatolik.")
        print(f"Movie detail error: {e}")


@router.message(F.text == "📝 Mening tarixim")
async def user_history_handler(message: Message):
    """Foydalanuvchi tomosha tarixi"""
    db_queries = DatabaseQueries()
    
    try:
        user = await db_queries.get_user_by_tg_id(message.from_user.id)
        if not user:
            await message.answer("❌ Foydalanuvchi topilmadi.")
            return
        
        # Foydalanuvchi tarixini olish
        history = await db_queries.get_user_movie_history(user.id, limit=20)
        
        if not history:
            await message.answer(
                "📝 <b>Tomosha Tarixi</b>\n\n"
                "❌ Siz hali hech qanday kino tomosha qilmagansiz.\n\n"
                "💡 Kino kodini yuborib, birinchi kinoyingizni tomosha qiling!",
                parse_mode="HTML"
            )
            return
        
        # Tarix matnini yaratish
        history_text = f"📝 <b>Sizning tomosha tarixingiz:</b>\n\n"
        
        for item in history[:10]:  # Faqat oxirgi 10 tasini ko'rsatish
            history_text += f"🎬 <b>{item['title']}</b>\n"
            history_text += f"   📝 Kod: <code>{item['code']}</code>\n"
            history_text += f"   📅 {item['viewed_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if len(history) > 10:
            history_text += f"... va yana {len(history) - 10} ta kino\n\n"
        
        # Statistika qo'shish
        total_watched = await db_queries.get_user_watched_movies_count(user.id)
        history_text += f"📊 <b>Jami tomosha qilganlar:</b> {total_watched} ta kino"
        
        await message.answer(history_text, parse_mode="HTML")
        
    except Exception as e:
        await message.answer("❌ Tarix yuklashda xatolik.")
        print(f"User history error: {e}")


@router.callback_query(F.data.startswith("page:"))
async def pagination_handler(callback: CallbackQuery):
    """Sahifalash handleri"""
    await callback.answer()
    
    try:
        page_data = callback.data.split(":")
        page_type = page_data[1]  # popular, recent, search
        page_num = int(page_data[2])
        
        db_queries = DatabaseQueries()
        
        # Sahifaga qarab kinolarni olish
        if page_type == "popular":
            movies = await db_queries.get_popular_movies(limit=10)
        elif page_type == "recent":
            movies = await db_queries.get_recent_movies(limit=10)
        else:
            # Search uchun query ni saqlab qolish kerak bo'ladi
            await callback.message.edit_text("❌ Sahifalash xatoligi.")
            return
        
        # Sahifa ma'lumotlarini hisoblash
        items_per_page = 5
        start_idx = (page_num - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_movies = movies[start_idx:end_idx]
        
        if not page_movies:
            await callback.message.edit_text("❌ Bu sahifada kinolar mavjud emas.")
            return
        
        # Matnni yangilash
        if page_type == "popular":
            text = f"📊 <b>Mashhur kinolar</b> (Sahifa {page_num}):\n\n"
        else:
            text = f"🆕 <b>Yangi kinolar</b> (Sahifa {page_num}):\n\n"
        
        for i, movie in enumerate(page_movies, start_idx + 1):
            text += f"{i}. <b>{movie.title}</b>\n"
            text += f"   📝 Kod: <code>{movie.code}</code>\n"
            text += f"   👁 Ko'rishlar: {movie.view_count}\n\n"
        
        # Yangi klaviatura
        total_pages = (len(movies) + items_per_page - 1) // items_per_page
        keyboard = get_pagination_keyboard(page_type, page_num, total_pages, page_movies)
        
        await callback.message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    except Exception as e:
        await callback.message.edit_text("❌ Sahifa yuklashda xatolik.")
        print(f"Pagination error: {e}")


def register_user_handlers(dp):
    """User handlerlarni ro'yxatga olish"""
    dp.include_router(router)