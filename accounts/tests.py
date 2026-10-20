from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .models import AuditLog, Role, User

PASSWORD = "Test-pass-98765"


def make_user(role, **kw):
    return User.objects.create_user(username=f"u_{role}", password=PASSWORD, role=role, **kw)


class RoleAccessTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_anonymous_redirected_to_login(self):
        resp = self.client.get(reverse("accounts:dashboard_teacher"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("accounts:login"), resp["Location"])

    def test_router_sends_each_role_to_its_dashboard(self):
        expected = {
            Role.SYSTEM_ADMIN: "accounts:dashboard_admin",
            Role.ACADEMIC_ADMIN: "accounts:dashboard_admin",
            Role.TEACHER: "accounts:dashboard_teacher",
            Role.ADVISOR: "accounts:dashboard_advisor",
            Role.STUDENT: "accounts:dashboard_student",
        }
        for role, url_name in expected.items():
            user = make_user(role)
            self.client.force_login(user)
            resp = self.client.get(reverse("accounts:dashboard"))
            self.assertRedirects(resp, reverse(url_name), fetch_redirect_response=False)
            self.client.logout()

    def test_student_cannot_open_teacher_or_admin_dashboard(self):
        self.client.force_login(make_user(Role.STUDENT))
        for name in ("accounts:dashboard_teacher", "accounts:dashboard_admin", "accounts:dashboard_advisor"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 403)

    def test_teacher_cannot_open_admin_dashboard(self):
        self.client.force_login(make_user(Role.TEACHER))
        self.assertEqual(self.client.get(reverse("accounts:dashboard_admin")).status_code, 403)

    def test_own_dashboard_renders(self):
        self.client.force_login(make_user(Role.TEACHER))
        self.assertEqual(self.client.get(reverse("accounts:dashboard_teacher")).status_code, 200)


class LoginTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = make_user(Role.TEACHER)

    def test_successful_login_is_audited(self):
        resp = self.client.post(reverse("accounts:login"), {"username": self.user.username, "password": PASSWORD})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(AuditLog.objects.filter(action="login", actor=self.user).exists())

    def test_failed_login_is_audited_without_password(self):
        self.client.post(reverse("accounts:login"), {"username": "u_teacher", "password": "wrong"})
        entry = AuditLog.objects.get(action="login_failed")
        self.assertNotIn("wrong", str(entry.detail))

    def test_lockout_after_repeated_failures(self):
        for _ in range(5):
            self.client.post(reverse("accounts:login"), {"username": "u_teacher", "password": "bad"})
        resp = self.client.post(reverse("accounts:login"), {"username": "u_teacher", "password": PASSWORD})
        self.assertEqual(resp.status_code, 429)  # even the correct password is refused while locked

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        self.client.post(reverse("accounts:logout"))
        self.assertTrue(AuditLog.objects.filter(action="logout").exists())


class MiscTests(TestCase):
    def test_superuser_becomes_system_admin(self):
        su = User.objects.create_superuser("root", "r@example.edu", PASSWORD)
        self.assertEqual(su.role, Role.SYSTEM_ADMIN)

    def test_health_endpoint(self):
        resp = self.client.get(reverse("health"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "ok"})

    def test_public_pages_render(self):
        for name in ("landing", "about", "features", "privacy", "contact"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
