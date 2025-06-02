"""
Statistika funksiyalar
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

from app.database import DatabaseQueries


async def get_platform_analytics(db_queries: DatabaseQueries, days: int = 30) -> Dict[str, Any]:
    """
    Platforma analitikasini olish
    
    Args:
        db_queries: Database queries instance
        days: Tahlil davri (kunlar)
    
    Returns:
        dict: Analitika ma'lumotlari
    """
    
    try:
        # Asosiy statistika
        platform_stats = await db_queries.get_platform_statistics()
        
        # Kunlik statistika
        daily_stats = await db_queries.get_daily_statistics(days=days)
        
        # Top kontentlar
        top_movies = await db_queries.get_top_movies(limit=10, days=days)
        
        # Faol foydalanuvchilar
        active_users = await db_queries.get_active_users(days=days, limit=20)
        
        # Analitik hisob-kitoblar
        analytics = {
            'overview': platform_stats,
            'daily_trends': calculate_trends(daily_stats),
            'content_performance': analyze_content_performance(top_movies),
            'user_engagement': analyze_user_engagement(active_users),
            'growth_metrics': calculate_growth_metrics(daily_stats),
            'period_summary': {
                'days_analyzed': days,
                'start_date': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'end_date': datetime.now().strftime('%Y-%m-%d')
            }
        }
        
        return analytics
        
    except Exception as e:
        print(f"Platform analytics error: {e}")
        return {}


def calculate_trends(daily_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Kunlik statistikadan trendlarni hisoblash
    
    Args:
        daily_stats: Kunlik statistika ma'lumotlari
    
    Returns:
        dict: Trend analitikasi
    """
    
    if not daily_stats or len(daily_stats) < 2:
        return {'trend': 'insufficient_data'}
    
    # So'nggi 7 kun va oldingi 7 kunni taqqoslash
    recent_period = daily_stats[:7]
    previous_period = daily_stats[7:14] if len(daily_stats) >= 14 else daily_stats[7:]
    
    recent_views = sum(day.get('total_views', 0) for day in recent_period)
    previous_views = sum(day.get('total_views', 0) for day in previous_period)
    
    recent_users = sum(day.get('unique_users', 0) for day in recent_period)
    previous_users = sum(day.get('unique_users', 0) for day in previous_period)
    
    # O'sish foizini hisoblash
    views_growth = calculate_percentage_change(previous_views, recent_views)
    users_growth = calculate_percentage_change(previous_users, recent_users)
    
    # Trend yo'nalishini aniqlash
    views_trend = 'up' if views_growth > 5 else 'down' if views_growth < -5 else 'stable'
    users_trend = 'up' if users_growth > 5 else 'down' if users_growth < -5 else 'stable'
    
    return {
        'views': {
            'growth_percentage': views_growth,
            'trend': views_trend,
            'recent_total': recent_views,
            'previous_total': previous_views
        },
        'users': {
            'growth_percentage': users_growth,
            'trend': users_trend,
            'recent_total': recent_users,
            'previous_total': previous_users
        },
        'daily_average': {
            'views': recent_views / len(recent_period) if recent_period else 0,
            'users': recent_users / len(recent_period) if recent_period else 0
        }
    }


def analyze_content_performance(top_movies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Kontent performance tahlili
    
    Args:
        top_movies: Top kinolar ma'lumotlari
    
    Returns:
        dict: Kontent tahlili
    """
    
    if not top_movies:
        return {'status': 'no_data'}
    
    total_views = sum(movie.get('views_count', 0) for movie in top_movies)
    total_unique_viewers = sum(movie.get('unique_viewers', 0) for movie in top_movies)
    
    # Eng mashhur kino
    top_movie = top_movies[0] if top_movies else None
    
    # O'rtacha ko'rish nisbati
    avg_views_per_movie = total_views / len(top_movies)
    avg_unique_per_movie = total_unique_viewers / len(top_movies)
    
    # Ko'rish sifati (unique/total nisbati)
    quality_ratio = (total_unique_viewers / total_views * 100) if total_views > 0 else 0
    
    return {
        'top_performer': {
            'title': top_movie.get('title', 'N/A') if top_movie else 'N/A',
            'views': top_movie.get('views_count', 0) if top_movie else 0,
            'unique_viewers': top_movie.get('unique_viewers', 0) if top_movie else 0
        },
        'averages': {
            'views_per_movie': avg_views_per_movie,
            'unique_per_movie': avg_unique_per_movie
        },
        'quality_metrics': {
            'overall_quality_ratio': quality_ratio,
            'total_content_pieces': len(top_movies)
        }
    }


def analyze_user_engagement(active_users: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Foydalanuvchi faollik tahlili
    
    Args:
        active_users: Faol foydalanuvchilar ma'lumotlari
    
    Returns:
        dict: Faollik tahlili
    """
    
    if not active_users:
        return {'status': 'no_data'}
    
    total_movies_watched = sum(user.get('movies_watched', 0) for user in active_users)
    avg_movies_per_user = total_movies_watched / len(active_users)
    
    # Eng faol foydalanuvchi
    top_user = max(active_users, key=lambda x: x.get('movies_watched', 0))
    
    # Faollik darajalari
    high_activity = len([u for u in active_users if u.get('movies_watched', 0) >= 10])
    medium_activity = len([u for u in active_users if 3 <= u.get('movies_watched', 0) < 10])
    low_activity = len([u for u in active_users if 1 <= u.get('movies_watched', 0) < 3])
    
    return {
        'top_user': {
            'name': top_user.get('full_name', 'N/A'),
            'movies_watched': top_user.get('movies_watched', 0)
        },
        'averages': {
            'movies_per_user': avg_movies_per_user,
            'total_active_users': len(active_users)
        },
        'activity_distribution': {
            'high_activity': high_activity,  # 10+ kinolar
            'medium_activity': medium_activity,  # 3-9 kinolar
            'low_activity': low_activity  # 1-2 kinolar
        }
    }


def calculate_growth_metrics(daily_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    O'sish metrikalarini hisoblash
    
    Args:
        daily_stats: Kunlik statistika
    
    Returns:
        dict: O'sish metrikalari
    """
    
    if len(daily_stats) < 7:
        return {'status': 'insufficient_data'}
    
    # Haftalik o'sish
    week1 = daily_stats[:7]
    week2 = daily_stats[7:14] if len(daily_stats) >= 14 else []
    
    week1_total = sum(day.get('total_views', 0) for day in week1)
    week2_total = sum(day.get('total_views', 0) for day in week2) if week2 else 0
    
    weekly_growth = calculate_percentage_change(week2_total, week1_total) if week2_total > 0 else 0
    
    # Kunlik o'rtacha o'sish
    daily_changes = []
    for i in range(1, min(len(daily_stats), 7)):
        prev_day = daily_stats[i].get('total_views', 0)
        curr_day = daily_stats[i-1].get('total_views', 0)
        if prev_day > 0:
            change = ((curr_day - prev_day) / prev_day) * 100
            daily_changes.append(change)
    
    avg_daily_growth = sum(daily_changes) / len(daily_changes) if daily_changes else 0
    
    return {
        'weekly_growth': weekly_growth,
        'daily_average_growth': avg_daily_growth,
        'growth_stability': calculate_growth_stability(daily_changes),
        'trend_direction': 'positive' if weekly_growth > 0 else 'negative' if weekly_growth < 0 else 'stable'
    }


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Foiz o'zgarishini hisoblash
    
    Args:
        old_value: Eski qiymat
        new_value: Yangi qiymat
    
    Returns:
        float: Foiz o'zgarishi
    """
    
    if old_value == 0:
        return 100.0 if new_value > 0 else 0.0
    
    return ((new_value - old_value) / old_value) * 100


def calculate_growth_stability(changes: List[float]) -> str:
    """
    O'sish barqarorligini hisoblash
    
    Args:
        changes: O'zgarishlar ro'yxati
    
    Returns:
        str: Barqarorlik darajasi
    """
    
    if not changes:
        return 'unknown'
    
    # Standart og'ish
    mean_change = sum(changes) / len(changes)
    variance = sum((x - mean_change) ** 2 for x in changes) / len(changes)
    std_deviation = variance ** 0.5
    
    # Barqarorlik darajasini aniqlash
    if std_deviation < 5:
        return 'very_stable'
    elif std_deviation < 15:
        return 'stable'
    elif std_deviation < 30:
        return 'moderate'
    else:
        return 'volatile'


async def generate_daily_report(db_queries: DatabaseQueries, date: Optional[datetime] = None) -> str:
    """
    Kunlik hisobot yaratish
    
    Args:
        db_queries: Database queries instance
        date: Hisobot sanasi (default: bugun)
    
    Returns:
        str: Kunlik hisobot matni
    """
    
    if date is None:
        date = datetime.now()
    
    try:
        # Bugungi statistika
        daily_stats = await db_queries.get_daily_statistics(days=1)
        today_data = daily_stats[0] if daily_stats else {}
        
        # Kechagi statistika bilan taqqoslash
        yesterday_stats = await db_queries.get_daily_statistics(days=2)
        yesterday_data = yesterday_stats[1] if len(yesterday_stats) > 1 else {}
        
        # Platform umumiy statistika
        platform_stats = await db_queries.get_platform_statistics()
        
        # O'zgarishlarni hisoblash
        views_change = calculate_percentage_change(
            yesterday_data.get('total_views', 0),
            today_data.get('total_views', 0)
        )
        
        users_change = calculate_percentage_change(
            yesterday_data.get('unique_users', 0),
            today_data.get('unique_users', 0)
        )
        
        # Hisobot yaratish
        report = f"""
📅 <b>Kunlik Hisobot - {date.strftime('%Y-%m-%d')}</b>

📊 <b>Bugungi faoliyat:</b>
• Ko'rishlar: {today_data.get('total_views', 0)} ({format_change(views_change)})
• Faol foydalanuvchilar: {today_data.get('unique_users', 0)} ({format_change(users_change)})
• Ko'rilgan kinolar: {today_data.get('unique_movies', 0)}

📈 <b>Umumiy holat:</b>
• Jami foydalanuvchilar: {platform_stats.get('total_users', 0)}
• Jami kinolar: {platform_stats.get('total_movies', 0)}
• Jami ko'rishlar: {platform_stats.get('total_views', 0)}

🎯 <b>Tahlil:</b>
{generate_daily_insights(today_data, yesterday_data, views_change, users_change)}

⏰ <b>Hisobot vaqti:</b> {datetime.now().strftime('%H:%M')}
"""
        
        return report
        
    except Exception as e:
        return f"❌ Kunlik hisobot yaratishda xatolik: {e}"


def format_change(change: float) -> str:
    """
    O'zgarishni formatlash
    
    Args:
        change: O'zgarish foizi
    
    Returns:
        str: Formatlanган o'zgarish
    """
    
    if change > 0:
        return f"📈 +{change:.1f}%"
    elif change < 0:
        return f"📉 {change:.1f}%"
    else:
        return "➡️ 0%"


def generate_daily_insights(today: Dict, yesterday: Dict, views_change: float, users_change: float) -> str:
    """
    Kunlik tahlil yaratish
    
    Args:
        today: Bugungi ma'lumotlar
        yesterday: Kechagi ma'lumotlar
        views_change: Ko'rishlar o'zgarishi
        users_change: Foydalanuvchilar o'zgarishi
    
    Returns:
        str: Tahlil matni
    """
    
    insights = []
    
    # Ko'rishlar tahlili
    if views_change > 10:
        insights.append("🔥 Ko'rishlar sezilarli darajada oshdi!")
    elif views_change > 0:
        insights.append("✅ Ko'rishlar o'sish trendida")
    elif views_change < -10:
        insights.append("⚠️ Ko'rishlar sezilarli kamaydi")
    else:
        insights.append("📊 Ko'rishlar barqaror")
    
    # Foydalanuvchilar tahlili
    if users_change > 15:
        insights.append("🚀 Faol foydalanuvchilar soni yuqori o'sdi!")
    elif users_change > 0:
        insights.append("👍 Foydalanuvchi faolligi oshmoqda")
    elif users_change < -15:
        insights.append("📉 Foydalanuvchi faolligi pasaydi")
    
    # Umumiy holat baholash
    overall_performance = (views_change + users_change) / 2
    if overall_performance > 10:
        insights.append("🎉 Ajoyib kun! Barcha ko'rsatkichlar yaxshi")
    elif overall_performance > 0:
        insights.append("😊 Ijobiy kun, davom eting!")
    elif overall_performance < -10:
        insights.append("🤔 Platformaga e'tibor berish kerak")
    
    return "\n".join(f"• {insight}" for insight in insights)


async def generate_weekly_summary(db_queries: DatabaseQueries) -> str:
    """
    Haftalik xulosa yaratish
    
    Args:
        db_queries: Database queries instance
    
    Returns:
        str: Haftalik xulosa
    """
    
    try:
        # So'nggi 7 kunlik ma'lumotlar
        daily_stats = await db_queries.get_daily_statistics(days=7)
        
        # Haftalik jami
        total_views = sum(day.get('total_views', 0) for day in daily_stats)
        total_unique_users = sum(day.get('unique_users', 0) for day in daily_stats)
        
        # Eng faol kun
        best_day = max(daily_stats, key=lambda x: x.get('total_views', 0)) if daily_stats else {}
        
        # Haftalik o'rtacha
        avg_daily_views = total_views / 7
        avg_daily_users = total_unique_users / 7
        
        summary = f"""
📊 <b>Haftalik Xulosa</b>
📅 {(datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')} - {datetime.now().strftime('%Y-%m-%d')}

🔢 <b>Jami ko'rsatkichlar:</b>
• Ko'rishlar: {total_views}
• Faol foydalanuvchilar: {total_unique_users}

📈 <b>Kunlik o'rtacha:</b>
• Ko'rishlar: {avg_daily_views:.1f}
• Foydalanuvchilar: {avg_daily_users:.1f}

🏆 <b>Eng faol kun:</b>
• Sana: {best_day.get('date', 'N/A')}
• Ko'rishlar: {best_day.get('total_views', 0)}

🎯 <b>Haftalik baholar:</b>
{generate_weekly_insights(daily_stats, total_views, total_unique_users)}
"""
        
        return summary
        
    except Exception as e:
        return f"❌ Haftalik xulosa yaratishda xatolik: {e}"


def generate_weekly_insights(daily_stats: List[Dict], total_views: int, total_users: int) -> str:
    """
    Haftalik tahlil yaratish
    
    Args:
        daily_stats: Kunlik statistika
        total_views: Jami ko'rishlar
        total_users: Jami foydalanuvchilar
    
    Returns:
        str: Haftalik tahlil
    """
    
    insights = []
    
    # Faollik darajasi
    if total_views > 1000:
        insights.append("🔥 Yuqori faollik haftaligi!")
    elif total_views > 500:
        insights.append("✅ Yaxshi faollik ko'rsatkichlari")
    elif total_views > 100:
        insights.append("📊 O'rtacha faollik darajasi")
    else:
        insights.append("📉 Past faollik, reklama kerak")
    
    # Barqarorlik
    view_counts = [day.get('total_views', 0) for day in daily_stats]
    max_views = max(view_counts) if view_counts else 0
    min_views = min(view_counts) if view_counts else 0
    
    if max_views > 0:
        stability = (min_views / max_views) * 100
        if stability > 70:
            insights.append("📈 Barqaror o'sish trendi")
        elif stability > 40:
            insights.append("📊 Nisbatan barqaror faollik")
        else:
            insights.append("📉 Faollikda katta tebranishlar")
    
    # Foydalanuvchi jalb etish
    if total_users > 100:
        insights.append("👥 Foydalanuvchilar faol ishtirok etmoqda")
    elif total_users > 50:
        insights.append("👤 Foydalanuvchi faolligi o'rtacha")
    else:
        insights.append("🎯 Foydalanuvchi jalb etishni kuchaytirish kerak")
    
    return "\n".join(f"• {insight}" for insight in insights)


def generate_performance_score(views: int, users: int, growth: float) -> Dict[str, Any]:
    """
    Performance ball yaratish
    
    Args:
        views: Ko'rishlar soni
        users: Foydalanuvchilar soni
        growth: O'sish foizi
    
    Returns:
        dict: Performance ballari
    """
    
    # Views score (0-40 ball)
    views_score = min(40, views / 25)  # Har 25 ta ko'rish uchun 1 ball
    
    # Users score (0-30 ball)
    users_score = min(30, users / 2)  # Har 2 ta foydalanuvchi uchun 1 ball
    
    # Growth score (0-30 ball)
    if growth > 0:
        growth_score = min(30, growth)  # Har 1% o'sish uchun 1 ball
    else:
        growth_score = max(-10, growth / 2)  # Kamayish uchun jazo
    
    total_score = views_score + users_score + growth_score
    
    # Daraja aniqlash
    if total_score >= 80:
        grade = "A+"
        status = "Ajoyib"
    elif total_score >= 70:
        grade = "A"
        status = "Yaxshi"
    elif total_score >= 60:
        grade = "B"
        status = "O'rtacha+"
    elif total_score >= 50:
        grade = "C"
        status = "O'rtacha"
    elif total_score >= 40:
        grade = "D"
        status = "Past"
    else:
        grade = "F"
        status = "Juda past"
    
    return {
        'total_score': round(total_score, 1),
        'views_score': round(views_score, 1),
        'users_score': round(users_score, 1),
        'growth_score': round(growth_score, 1),
        'grade': grade,
        'status': status
    }


async def export_analytics_report(db_queries: DatabaseQueries, days: int = 30) -> Dict[str, Any]:
    """
    Analitika hisobotini eksport qilish
    
    Args:
        db_queries: Database queries instance
        days: Tahlil davri
    
    Returns:
        dict: To'liq analitika hisoboti
    """
    
    try:
        # To'liq analitika
        analytics = await get_platform_analytics(db_queries, days)
        
        # Qo'shimcha ma'lumotlar
        dashboard_data = await db_queries.get_admin_dashboard_data()
        
        # Eksport uchun formatlanган hisobot
        export_data = {
            'report_info': {
                'generated_at': datetime.now().isoformat(),
                'period_days': days,
                'report_type': 'full_analytics'
            },
            'analytics': analytics,
            'dashboard_data': dashboard_data,
            'summary': {
                'total_users': dashboard_data['platform_stats']['total_users'],
                'total_movies': dashboard_data['platform_stats']['total_movies'],
                'total_views': dashboard_data['platform_stats']['total_views'],
                'active_channels': dashboard_data['platform_stats']['active_channels']
            }
        }
        
        return export_data
        
    except Exception as e:
        print(f"Export analytics error: {e}")
        return {'error': str(e)}