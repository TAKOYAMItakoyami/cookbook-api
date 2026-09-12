import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загрузка ингредиентов из CSV-файла"

    def handle(self, *args, **options):
        self.stdout.write("Начинаю загрузку ингредиентов...")

        csv_file = settings.BASE_DIR / "data" / "ingredients.csv"

        if not csv_file.exists():
            self.stdout.write(self.style.ERROR(f"Файл не найден: {csv_file}"))
            return

        created = 0
        existing = 0

        with open(csv_file, encoding="utf-8", newline="") as file:
            reader = csv.reader(file)

            for row in reader:
                if len(row) != 2:
                    continue

                name, measurement_unit = row

                _, is_created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit,
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
