from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

from .audit import record_audit


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    record_audit("login", actor=user, request=request)


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    record_audit("logout", actor=user, request=request)


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request=None, **kwargs):
    # Store only the attempted username, never the password.
    record_audit("login_failed", request=request, username=str(credentials.get("username", ""))[:150])
