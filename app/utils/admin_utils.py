"""
Admin yordamchi funksiyalar
"""

import json
import os
import csv
from datetime import datetime
from typing import Dict, Any, List
from io import StringIO

from app.database.models import User, Movie, Channel


def format_admin_stats(dashboard_data: Dict[str, Any]) -> str:
    """
    Admin statistikasini formatlash
    
    Args:
        dashboard_data: Dashboard ma'lumotlari
    
    Returns:
        str: Formatlanган statistika
    """
    
    stats = dashboard_data['platform_stats']
    top_movies = dashboard_data['top_movies']
    active_users = dashboard_data['active_users']
    daily_stats = dashboard_data['daily_stats']
    
    admin_stats = f"""
📊 <b>Batafsil Platforma Statistikasi</b>

👥 <b>Foydalanuvchilar:</b>
• Jami: {stats['total_users']}
• Bugun faol: {stats['active_users_24h']}
• Yangi (hafta): {stats['new_users_week']}
• Adminlar: {stats['admin_count']}

🎬 <b>Kontent:</b>
• Jami kinolar: {stats['total_movies']}
• Jami ko'rishlar: {stats['total_views']}
• Faol kanallar: {stats['active_channels']}

🔥 <b>Top kinolar (hafta):</b>
"""
    
    for i, movie_data in enumerate(top_movies[:5], 1):
        admin_stats += f"{i}. {movie_data['title']} ({movie_data['views_count']} ko'rish)\n"
    
    admin_stats += "\n🚀 <b>Eng faol foydalanuvchilar:</b>\n"
    
    for i, user_data in enumerate(active_users[:5], 1):
        admin_stats += f"{i}. {user_data['full_name']} ({user_data['movies_watched']} kino)\n"
    
    if daily_stats:
        admin_stats += f"\n📈 <b>Bugungi statistika:</b>\n"
        today_stats = daily_stats[0] if daily_stats else {}
        admin_stats += f"• Ko'rishlar: {today_stats.get('total_views', 0)}\n"
        admin_stats += f"• Faol foydalanuvchilar: {today_stats.get('unique_users', 0)}\n"
        admin_stats += f"• Ko'rilgan kinolar: {today_stats.get('unique_movies', 0)}"
    
    return admin_stats


async def export_data_to_file(backup_data: Dict[str, Any], format_type: str = 'json') -> str:
    """
    Ma'lumotlarni faylga eksport qilish
    
    Args:
        backup_data: Backup ma'lumotlari
        format_type: Fayl formati (json, csv)
    
    Returns:
        str: Fayl yo'li
    """
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format_type == 'json':
        filename = f"backup_{timestamp}.json"
        filepath = os.path.join("exports", filename)
        
        # Exports papkasini yaratish
        os.makedirs("exports", exist_ok=True)
        
        # JSON faylga yozish
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=4)
        return filepath
    
    