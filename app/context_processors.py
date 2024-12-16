# app/context_processors.py
from .views import get_current_user

def add_role_and_user_id(request):
    current_user, role_name = get_current_user(request)
    context = {
        'role': role_name,
        'user_id': current_user.id if current_user else None,
    }
    if role_name in ['employee', 'admin'] and current_user:
        context['employee_id'] = current_user.id
    return context
