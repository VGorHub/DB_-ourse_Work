# app/context_processors.py

def add_role_and_user_id(request):
    return {
        'role': request.session.get('role', 'user'),
        'user_id': request.session.get('user_id', ''),
    }
