from django.core.management.base import BaseCommand

from iam.models import Role


class Command(BaseCommand):
    help = "Crea los roles base para PixelCheck"

    def handle(self, *args, **options):
        created = 0
        for role in Role.RoleName.values:
            _, was_created = Role.objects.get_or_create(name=role)
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Roles sincronizados. Nuevos: {created}"))
