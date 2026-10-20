from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"


def msg(title, message):
    return {"title": title, "message": message}


urlpatterns = [
    path("login/", views.RateLimitedLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),  # POST only
    path("dashboard/", views.dashboard_router, name="dashboard"),
    path("dashboard/admin/", views.dashboard_admin, name="dashboard_admin"),
    path("dashboard/teacher/", views.dashboard_teacher, name="dashboard_teacher"),
    path("dashboard/advisor/", views.dashboard_advisor, name="dashboard_advisor"),
    path("dashboard/student/", views.dashboard_student, name="dashboard_student"),
    path("password-change/", auth_views.PasswordChangeView.as_view(
        template_name="accounts/form_page.html",
        success_url=reverse_lazy("accounts:password_change_done"),
        extra_context=msg("Change password", "")), name="password_change"),
    path("password-change/done/", auth_views.PasswordChangeDoneView.as_view(
        template_name="accounts/form_page.html",
        extra_context=msg("Password changed", "Your password was updated.")), name="password_change_done"),
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="accounts/form_page.html",
        email_template_name="accounts/password_reset_email.txt",
        subject_template_name="accounts/password_reset_subject.txt",
        success_url=reverse_lazy("accounts:password_reset_done"),
        extra_context=msg("Reset your password", "Enter your account email and we will send a reset link.")),
        name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="accounts/form_page.html",
        extra_context=msg("Check your email", "If an account exists for that address, a reset link has been sent.")),
        name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="accounts/form_page.html",
        success_url=reverse_lazy("accounts:password_reset_complete"),
        extra_context=msg("Choose a new password", "")), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="accounts/form_page.html",
        extra_context=msg("Password reset", "Your password has been reset. You can now sign in.")),
        name="password_reset_complete"),
]
