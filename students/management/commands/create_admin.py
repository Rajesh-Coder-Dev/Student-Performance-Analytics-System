from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Creates or resets an administrator superuser account"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            default="admin",
            help="Administrator username (default: 'admin')",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="admin123",
            help="Administrator password (default: 'admin123')",
        )
        parser.add_argument(
            "--email",
            type=str,
            default="admin@example.com",
            help="Administrator email (default: 'admin@example.com')",
        )

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        email = options["email"]

        user, created = User.objects.get_or_create(username=username)

        user.email = email
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Administrator '{username}' created successfully!"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Administrator '{username}' already existed; password & admin privileges updated successfully!"
                )
            )

        self.stdout.write(f"Username: {username}")
        self.stdout.write(f"Email:    {email}")
        self.stdout.write(f"Password: {password}")
