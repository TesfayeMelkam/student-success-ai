from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.shortcuts import redirect, render

from .audit import client_ip, record_audit
from .models import Role
from .permissions import ADMIN_ROLES, role_required

PUBLIC_PAGES = {
    "about": {
        "title": "About the platform",
        "sections": [
            ("Purpose", "Student Success AI helps educators notice academic difficulty early and "
                        "document the support they provide. Predictions are estimates that inform "
                        "a human review. They are never final judgments about a student."),
            ("Status", "This is a university-project build developed in phases. Features appear "
                       "in the application only once they are implemented and tested."),
        ],
    },
    "features": {
        "title": "Features and capabilities",
        "sections": [
            ("Available now", "Role-based sign-in, audit logging, login protection, and role dashboards."),
            ("Planned phases", "Student and course records, attendance and assessments, score and "
                               "support-need models with evaluation reports, explanations, a review "
                               "queue, support plans, learning-resource recommendations, analytics, "
                               "and a versioned REST API."),
        ],
    },
    "privacy": {
        "title": "Privacy and security",
        "sections": [
            ("Access control", "Every page checks the signed-in user's role on the server. Students "
                               "will see only their own records; teachers only their assigned courses."),
            ("Accountability", "Sign-ins and failed sign-ins are written to an audit log. "
                               "Passwords are hashed by Django and are never stored in plain text."),
            ("Predictions", "Model outputs will never trigger automatic penalties, exclusions, or labels."),
        ],
    },
    "contact": {
        "title": "Contact",
        "sections": [
            ("Support", "Contact your institution's system administrator for account access or "
                        "record corrections. A contact form is not part of this build."),
        ],
    },
}


def public_page(request, slug):
    return render(request, "landing/page.html", PUBLIC_PAGES[slug] | {"slug": slug})


def permission_denied(request, exception=None):
    return render(request, "403.html", status=403)


class RateLimitedLoginView(LoginView):
    """Locks a (IP, username) pair after too many failures for a cooling-off period."""

    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def _key(self, request, username):
        return f"login-fail:{client_ip(request)}:{username.strip().lower()}"

    def post(self, request, *args, **kwargs):
        key = self._key(request, request.POST.get("username", ""))
        if cache.get(key, 0) >= settings.LOGIN_MAX_ATTEMPTS:
            record_audit("login_blocked", request=request, username=request.POST.get("username", "")[:150])
            context = self.get_context_data(form=self.get_form(), locked=True)
            return self.render_to_response(context, status=429)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        key = self._key(self.request, self.request.POST.get("username", ""))
        cache.add(key, 0, settings.LOGIN_LOCKOUT_SECONDS)
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1, settings.LOGIN_LOCKOUT_SECONDS)
        return super().form_invalid(form)

    def form_valid(self, form):
        cache.delete(self._key(self.request, self.request.POST.get("username", "")))
        return super().form_valid(form)


DASHBOARD_URLS = {
    Role.SYSTEM_ADMIN: "accounts:dashboard_admin",
    Role.ACADEMIC_ADMIN: "accounts:dashboard_admin",
    Role.TEACHER: "accounts:dashboard_teacher",
    Role.ADVISOR: "accounts:dashboard_advisor",
    Role.STUDENT: "accounts:dashboard_student",
}


@login_required
def dashboard_router(request):
    return redirect(DASHBOARD_URLS[request.user.role])


def _dashboard(request, title, blurb, upcoming):
    return render(request, "dashboard/home.html", {"title": title, "blurb": blurb, "upcoming": upcoming})


@role_required(*ADMIN_ROLES)
def dashboard_admin(request):
    return _dashboard(
        request, "Administration",
        "Manage users, departments, courses, and model governance.",
        ["Student and course records (Phase 2)", "Model versions and evaluation (Phases 3-4)",
         "Audit log review (available now in the Django admin)"],
    )


@role_required(Role.TEACHER)
def dashboard_teacher(request):
    return _dashboard(
        request, "Teaching",
        "Review your assigned courses and the students who may benefit from attention.",
        ["Your courses and gradebook (Phase 2)", "Review queue (Phase 6)"],
    )


@role_required(Role.ADVISOR)
def dashboard_advisor(request):
    return _dashboard(
        request, "Advising",
        "Follow the students you advise and track their support plans.",
        ["Advisee overview (Phase 2)", "Support plans and follow-ups (Phase 6)"],
    )


@role_required(Role.STUDENT)
def dashboard_student(request):
    return _dashboard(
        request, "My progress",
        "See your own results, attendance, and recommended learning resources.",
        ["Your grades and attendance (Phase 2)", "Recommended resources (Phase 6)"],
    )
