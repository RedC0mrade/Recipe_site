import csv
import os

from recipes.models import Ingredient

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(current_dir, 'data', 'ingredients.csv')


def run():
    """
    Скрипт для заполнения базы данных ингредиентами.

    Выполнить команду python manage.py runscript my_script -v2.
    """
    with open(csv_file_path, encoding='utf8') as f:
        reader = csv.reader(f)
        data = []
        for row in reader:
            obj = Ingredient()
            obj.name = row[0]
            obj.measurement_unit = row[1]
            data.append(obj)
        Ingredient.objects.bulk_create(data)
