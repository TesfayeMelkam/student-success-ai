from django.contrib import admin
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import TemplateView

from accounts.views import public_page

handler403 = "accounts.views.permission_denied"


def health(request):
    """Liveness + database check for load balancers. Exposes no private data."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok"})
    except Exception:
        return JsonResponse({"status": "database_unavailable"}, status=503)


urlpatterns = [
    path("", TemplateView.as_view(template_name="landing/index.html"), name="landing"),
    path("about/", public_page, {"slug": "about"}, name="about"),
    path("features/", public_page, {"slug": "features"}, name="features"),
    path("privacy/", public_page, {"slug": "privacy"}, name="privacy"),
    path("contact/", public_page, {"slug": "contact"}, name="contact"),
    path("health/", health, name="health"),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
]
