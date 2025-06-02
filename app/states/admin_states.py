"""
Admin FSM holatlari
"""

from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Admin FSM holatlari"""
    
    # Kino qo'shish holatlari
    waiting_movie_video = State()
    waiting_movie_private_message_id = State()
    waiting_movie_code = State()
    waiting_movie_title = State()
    waiting_movie_description = State()
    
    # Kino tahrirlash holatlari
    editing_movie_select = State()
    editing_movie_field = State()
    editing_movie_value = State()
    
    # Kanal qo'shish holatlari
    waiting_channel_title = State()
    waiting_channel_link = State()
    waiting_channel_username = State()
    waiting_channel_status = State()
    
    # Kanal boshqarish holatlari
    managing_channel_select = State()
    managing_channel_action = State()
    
    # Foydalanuvchi boshqarish holatlari
    searching_users = State()
    selecting_user_action = State()
    waiting_user_id = State()
    waiting_admin_confirmation = State()
    
    # Xabar yuborish holatlari
    broadcast_preparing = State()
    broadcast_message = State()
    broadcast_confirmation = State()
    broadcast_target_selection = State()
    
    # Statistika holatlari
    stats_period_selection = State()
    stats_detailed_view = State()
    stats_export_format = State()
    
    # Eksport holatlari
    export_data_selection = State()
    export_format_selection = State()
    export_confirmation = State()
    
    # Sistema sozlamalari holatlari
    settings_category = State()
    settings_parameter = State()
    settings_value = State()
    settings_confirmation = State()
    
    # Kino o'chirish holatlari
    deleting_movie_search = State()
    deleting_movie_select = State()
    deleting_movie_confirmation = State()
    
    # Kanal o'chirish holatlari
    deleting_channel_select = State()
    deleting_channel_confirmation = State()
    
    # Foydalanuvchini bloklash holatlari
    blocking_user_search = State()
    blocking_user_select = State()
    blocking_user_reason = State()
    blocking_user_confirmation = State()
    
    # Admin qilish holatlari
    promoting_user_search = State()
    promoting_user_select = State()
    promoting_user_confirmation = State()
    
    # Bulk operatsiyalar holatlari
    bulk_operation_type = State()
    bulk_operation_selection = State()
    bulk_operation_confirmation = State()
    
    # Hisobot yaratish holatlari
    report_type_selection = State()
    report_period_selection = State()
    report_parameters = State()
    report_generation = State()
    
    # Backup holatlari
    backup_type_selection = State()
    backup_confirmation = State()
    restore_file_upload = State()
    restore_confirmation = State()
    
    # Debug holatlari
    debug_query_input = State()
    debug_command_execution = State()
    
    # Maintenance holatlari
    maintenance_action_selection = State()
    maintenance_confirmation = State()
    maintenance_execution = State()