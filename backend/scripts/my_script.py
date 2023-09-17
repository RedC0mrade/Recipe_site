import csv

from recipes.models import Ingredient


def run():
    """python manage.py runscript my_script -v2"""
    with open('D:/Dev/foodgram-project-react/data/ingredients.csv',
              encoding='utf8') as f:
        reader = csv.reader(f)
        data = []
        for row in reader:
            obj = Ingredient()
            obj.name = row[0]
            obj.measurement_unit = row[1]
            data.append(obj)
        Ingredient.objects.bulk_create(data)

