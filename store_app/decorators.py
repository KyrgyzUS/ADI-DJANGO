# decorators.py
from django.shortcuts import redirect

def role_required(*required_roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            user_role = request.session.get('user_role')
            if user_role in required_roles:
                return view_func(request, *args, **kwargs)
            return redirect('login')
        return _wrapped_view
    return decorator
