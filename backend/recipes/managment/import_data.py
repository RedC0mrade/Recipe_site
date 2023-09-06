import csv

from django.core.management.base import BaseCommand

from backend.recipes.models import Ingredient

CSV_PATH = 'data/'
FOREIGN_KEY_FIELDS = ('category', 'author')
DICT = {Ingredient: 'ingredients.csv'}


def csv_import(csv_data, model):
    """Импорт данных из CSV-файла в базу данных."""

    objects = []
    for row in csv_data:
        objects.append(model(**row))
    model.objects.bulk_create(objects)


class Command(BaseCommand):
    help = 'импорт из .csv'

    def handle(self, *args, **kwargs):
        for model in DICT:
            with open(
                CSV_PATH + DICT[model],
                newline='',
                encoding='utf8'
            ) as csv_file:
                csv_import(csv.DictReader(csv_file), model)
        self.stdout.write(
            self.style.SUCCESS(
                'Загрузка завершена'
            )
        )
