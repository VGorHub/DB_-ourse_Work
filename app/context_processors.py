# app/context_processors.py
from .models import Employee
from .views import get_current_user

def add_role_and_user_id(request):
    app_user, role_name = get_current_user(request)
    context = {
        'role': role_name,
        'user_id': app_user.id if app_user else None,
    }
    if app_user.role in ['admin', 'employee']:
        try:
            employee = Employee.objects.get(user=app_user)
            context['employee_id'] = employee.id
        except Employee.DoesNotExist:
            context['employee_id'] = None
    else:
        context['employee_id'] = None
    return context
