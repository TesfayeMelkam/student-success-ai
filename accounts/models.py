from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    SYSTEM_ADMIN = "system_admin", "System Administrator"
    ACADEMIC_ADMIN = "academic_admin", "Academic Administrator"
    TEACHER = "teacher", "Teacher / Lecturer"
    ADVISOR = "advisor", "Academic Advisor"
    STUDENT = "student", "Student"


class User(AbstractUser):
    """Custom user with one role. Authorization always checks this on the server."""

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT, db_index=True)

    def save(self, *args, **kwargs):
        # Superusers created via `createsuperuser` should be system administrators.
        if self.is_superuser and self.role == Role.STUDENT:
            self.role = Role.SYSTEM_ADMIN
        super().save(*args, **kwargs)

    @property
    def is_admin_role(self):
        return self.role in (Role.SYSTEM_ADMIN, Role.ACADEMIC_ADMIN)

    @property
    def is_teacher(self):
        return self.role == Role.TEACHER

    @property
    def is_advisor(self):
        return self.role == Role.ADVISOR

    @property
    def is_student(self):
        return self.role == Role.STUDENT


class AuditLog(models.Model):
    """Append-only record of sensitive actions (logins, failed logins, later: exports, edits)."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_entries"
    )
    action = models.CharField(max_length=60, db_index=True)
    detail = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%Y-%m-%d %H:%M} {self.action}"
