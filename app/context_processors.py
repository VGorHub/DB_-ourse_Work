# app/context_processors.py

from .views import get_current_user

def add_role_and_user_id(request):
    app_user, role_name = get_current_user(request)
    return {
        'role': role_name,
        'user_id': app_user.id if app_user else None,
    }
