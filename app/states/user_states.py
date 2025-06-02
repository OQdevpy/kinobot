"""
Foydalanuvchi FSM holatlari
"""

from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """Foydalanuvchi FSM holatlari"""
    
    # Qidirish holatlari
    waiting_search_query = State()
    search_results_viewing = State()
    search_filter_selection = State()
    search_advanced_options = State()
    
    # Kino ko'rish holatlari
    movie_code_input = State()
    movie_watching = State()
    movie_rating = State()
    movie_feedback = State()
    
    # Obuna holatlari
    checking_subscription = State()
    joining_channels = State()
    verifying_subscription = State()
    subscription_complete = State()
    
    # Profil holatlari
    profile_viewing = State()
    profile_editing = State()
    profile_settings = State()
    
    # Tarix holatlari
    history_viewing = State()
    history_filtering = State()
    history_clearing = State()
    
    # Sevimlilar holatlari
    favorites_viewing = State()
    favorites_managing = State()
    favorites_organizing = State()
    
    # Tavsiyalar holatlari
    recommendations_viewing = State()
    recommendations_filtering = State()
    
    # Ulashish holatlari
    sharing_movie = State()
    sharing_platform = State()
    sharing_message = State()
    
    # Shikoyat holatlari
    complaint_category = State()
    complaint_description = State()
    complaint_submission = State()
    
    # Yordam holatlari
    help_category = State()
    help_question = State()
    
    # Sozlamalar holatlari
    settings_category = State()
    settings_parameter = State()
    settings_confirmation = State()
    
    # Notifikatsiya holatlari
    notification_preferences = State()
    notification_channels = State()
    
    # Til holatlari
    language_selection = State()
    language_confirmation = State()
    
    # Feedback holatlari
    feedback_type = State()
    feedback_message = State()
    feedback_rating = State()
    feedback_submission = State()
    
    # Kategoriya tanlash holatlari
    category_selection = State()
    subcategory_selection = State()
    
    # Playlist holatlari (kelajakda)
    playlist_creation = State()
    playlist_naming = State()
    playlist_managing = State()
    
    # Download holatlari (agar kerak bo'lsa)
    download_request = State()
    download_quality = State()
    download_confirmation = State()
    
    # Takroriy tomosha holatlari
    watch_later_adding = State()
    watch_later_viewing = State()
    watch_later_organizing = State()
    
    # Premium holatlari (kelajakda)
    premium_info_viewing = State()
    premium_subscription = State()
    premium_payment = State()
    
    # Statistika holatlari
    personal_stats_viewing = State()
    stats_period_selection = State()
    
    # Import/Export holatlari
    data_export_request = State()
    data_import_upload = State()
    
    # Obuna bekor qilish holatlari
    unsubscribe_reason = State()
    unsubscribe_confirmation = State()
    
    # Blokdan chiqarish so'rovi holatlari
    unblock_request = State()
    unblock_reason = State()
    unblock_appeal = State()