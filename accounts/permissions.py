"""Server-side role checks. Hiding a button is never the only protection."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import Role


def role_required(*roles):
    """Allow only logged-in users whose role is listed; others get HTTP 403."""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapped

    return decorator


ADMIN_ROLES = (Role.SYSTEM_ADMIN, Role.ACADEMIC_ADMIN)
