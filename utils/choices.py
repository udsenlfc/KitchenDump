import os
import re
import json
import pandas as pd

### Load the .json dataset
DATASET_PATH = os.path.join(os.path.dirname(__file__), '..', 'dataset', 'recipes.json')

with open(DATASET_PATH, 'r', encoding="UTF8") as f:
    data = json.load(f)

df = pd.json_normalize(data)

### Converts a string with underscore to a string with space and capitalizes the first letter.
### E.g. "olive_oil" to "Olive oil"
def get_label_name(string):
    return string.replace("_", " ").capitalize()

### Converts a string to a valid attribute name.
### E.g. "Olive Oil!" to "olive_oil"
def to_attr_name(string):
    s = string.lower()
    s = re.sub(r'[^a-z0-9_]', '_', s)
    s = re.sub(r'_+', '_', s)
    return s.strip('_')

### Creates a class with attributes from a list of strings.
class ModelChoices:
    def __init__(self, choices_list):
        for item in choices_list:
            setattr(self, to_attr_name(item), item)

    def choices(self):
        return [(k, v) for k, v in self.__dict__.items()]

    def values(self):
        return [v for v in self.__dict__.keys()]

    def labels(self):
        return [l for l in self.__dict__.values()]


### Collects unique tags across all recipes
RecipeTagChoices = ModelChoices(
    pd.Series([tag for recipe in data for tag in (recipe['tags'] or [])]).unique()
)

### Collects unique ingredient names across all recipes
RecipeIngredientChoices = ModelChoices(
    pd.Series([i['name'] for recipe in data for i in (recipe['ingredients'] or [])]).unique()
)

if __name__ == '__main__':
    print(f"Loaded {len(data)} recipes")
    print("\nSample tags:", RecipeTagChoices.labels()[:5])
    print("Sample ingredients:", RecipeIngredientChoices.labels()[:5])

