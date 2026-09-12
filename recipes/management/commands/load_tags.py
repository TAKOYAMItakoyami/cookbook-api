import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = "Загрузка тегов из CSV-файла"

    def handle(self, *args, **options):
        self.stdout.write("Начинаю загрузку тегов...")

        csv_file = settings.BASE_DIR / "data" / "tags.csv"

        if not csv_file.exists():
            self.stdout.write(self.style.ERROR(f"Файл не найден: {csv_file}"))
            return

        created = 0
        existing = 0

        with open(csv_file, encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)

            for row in reader:
                _, is_created = Tag.objects.get_or_create(
                    name=row["name"],
                    defaults={"slug": row["slug"]},
                )

                if is_created:
                    created += 1
                else:
                    existing += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Загрузка завершена.\n"
                f"Создано: {created}\n"
                f"Уже существовало: {existing}"
            )
        )
