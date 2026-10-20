from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from accounts.models import Role, User

DEMO_PASSWORD = "DemoPass-12345"  # DEMO ONLY. Works only when DEBUG is on.


class Command(BaseCommand):
    help = "Create one DEMO user per role for local development (refuses to run when DEBUG is off)."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_demo_users only runs in development (DEBUG=True).")
        for role in Role.values:
            user, created = User.objects.get_or_create(
                username=f"demo_{role}", defaults={"role": role, "email": f"demo_{role}@example.edu"}
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
            self.stdout.write(f"{'created' if created else 'exists '} demo_{role}")
        self.stdout.write(self.style.WARNING(f"DEMO accounts, password: {DEMO_PASSWORD}"))
