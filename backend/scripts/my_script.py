import csv
import os

from recipes.models import Ingredient, Tags

current_dir = os.path.dirname(os.path.abspath(__file__))
csv_file_path = os.path.join(current_dir, 'ingredients.csv')

TAGS_NAMES = ('Breakfast', 'Lunch', 'Dinner')
TAGS_COLORS = ('#808080', '#FF00FF', '#C0C0C0')
TAGS_SLUG = ('breakfast', 'lunch', 'dinner')


def run():
    """
    Скрипт для заполнения базы данных ингредиентами и тэгов.

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

    tags_data = []
    for i in range(3):
        obj = Tags()
        obj.name = TAGS_NAMES[i]
        obj.slug = TAGS_SLUG[i]
        obj.color = TAGS_COLORS[i]
        tags_data.append(obj)
    Tags.objects.bulk_create(tags_data)
