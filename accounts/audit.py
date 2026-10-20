def client_ip(request):
    """REMOTE_ADDR only. X-Forwarded-For is client-controlled, so it is not trusted by default."""
    return request.META.get("REMOTE_ADDR") if request else None


def record_audit(action, actor=None, request=None, **detail):
    from .models import AuditLog

    return AuditLog.objects.create(
        actor=actor if getattr(actor, "pk", None) else None,
        action=action,
        detail=detail,
        ip_address=client_ip(request),
    )
