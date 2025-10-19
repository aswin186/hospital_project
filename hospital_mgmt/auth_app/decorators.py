from functools import wraps
from django.shortcuts import redirect

def session_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('user_id'):
            # User is logged in, proceed to the view
            return view_func(request, *args, **kwargs)
        # User not logged in, redirect to login page
        return redirect('auth_login')  # Replace with your login URL if different
    return wrapper
