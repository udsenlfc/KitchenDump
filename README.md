# KitchenDump

KitchenDump is a web application that helps you find recipes based on the ingredients you already have at home. Instead of searching for a specific recipe, you tell KitchenDump what's in your fridge and pantry - and it returns recipes ranked by how many of the required ingredients you already have, minimizing what you need to buy.

## Stack

- **Backend:** Python 3, Flask
- **Database:** PostgreSQL 16
- **Frontend:** HTML, CSS
- **Infrastructure:** Docker
- **Libraries:** psycopg2, pandas, python-dotenv

## Installation and setup

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Python 3.10+ with pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/udsenlfc/KitchenDump.git
cd KitchenDump

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Start the database
docker compose up -d db

# 4. Wait ~5 seconds, then fill the database (run once)
python utils/init_db.py

# 5. Start the Flask application
flask --app app run --debug

# 5a. Known Issue, if flask and python are in different folders, do instead:
python -m flask --app app run --debug
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

> **Note:** If you have Postgres.app installed, stop it before running Docker — both using port 5432 is a known issue, Postgres was prioritised.

## Features

- **Ingredient search**: Enter ingredients as comma-separated text; results are ranked by coverage percentage (how many of the recipe's ingredients you already have).
- **Use Kitchen**: Automatically includes all ingredients saved in your pantry and fridge when searching.
- **Recipe detail view**: Shows cooking time, servings, ingredients, step-by-step instructions and tags.
- **My Kitchen**: Manage your pantry and fridge; ingredients saved here are automatically included in kitchen searches.
- **Autocomplete**: Ingredient suggestions as you type, matched against the database. This ensures you don't type ingredients which are not present in the database.
- **Favorites**: Save and remove your favorite recipes across sessions.
- **Navigation Bar**: Navigate between the pages of the application.

## Database design

The database consists of 6 tables derived from the ER diagram:

- `recipes`: Core recipe data: name, cooking time, servings, description, instructions
- `ingredients`: All unique ingredient names extracted from the recipes
- `recipe_ingredients`: Many-to-many relation between recipes and ingredients, with quantity, unit and raw display string
- `tags`: All unique tags extracted from the recipes 
- `recipe_tags`: Many-to-many relation between recipes and tags
- `storage`: User's saved pantry and fridge ingredients
- `favorites`: User's saved favorite recipes

The dataset is sourced from Kaggle: https://www.kaggle.com/datasets/seungyeonhan1/recipe-dataset-with-images-tags-and-ratings/data. It contains ~21K recipes with images, however for the use case and due to thehuge sizing, the images were cut, as well as a random set of 1000 recipes were picked from the set.

The raw dataset stores ingredients as unstructured strings such as "1 1/2 cups low-sodium chicken broth". To structure these into separate fields (quantity, unit, name) as well as the original "raw" string for display usage, the Python library `ingredient-parser-nlp` was used during dataset preparation. This library applies a trained NLP model to parse ingredient strings into structured components. The parsed output forms the basis of the `recipe_ingredients` table schema.

### Regex usage

Regex is used in two places in the project:

1. Input normalisation in `choices.py`:
The `to_attr_name` function uses regex to convert arbitrary ingredient and tag strings from the dataset into valid Python attribute names.

2. Ingredient matching in `queries.py`:
Ingredient search uses PostgreSQL's `ILIKE ANY(%s)` operator with patterns constructed in Python. Each user-supplied ingredient is wrapped in `%` before being passed to the query.

## Considerations regarding design and further improvements

Several attributes in the schema are included intentionally even though they are not actively used in the current version of the application. These represent deliberate design choices rather than oversights. They are simply not used due to time restrictions. This includes the following:

**`quantity` and `unit` in `recipe_ingredients`**:
These fields are populated from the original dataset and preserved to maintain data fidelity. They are not used in the current search logic, but would be essential for future features such as a shopping list generator ("you have 1 cup flour, the recipe needs 2") or portion-adjusted ingredient views.

**`raw` in `recipe_ingredients`**:
The original dataset stores ingredients as formatted strings such as "1 1/2 cups low-sodium chicken broth". Normalising these into separate quantity, unit and name fields would lose formatting details. The `raw` field preserves the original string for display purposes, while `name` is used for matching — a deliberate separation of display data and query data.

**`quantity` and `unit` in `storage`**:
Included to support a potential future feature where the user can record how much of an ingredient they have. This would enable more precise matching — for example, filtering out recipes that require more of an ingredient than the user currently has. In the current version, only the ingredient name is used for search.

**`category` in `storage`**:
The `category` field allows users to organise ingredients in My Kitchen into two groups: Pantry and Fridge. The original intention was for this distinction to reflect how frequently an ingredient needs replenishing - shelf-stable items like spices and oils would belong in Pantry, while perishables like milk and bread would go in Fridge. This separation could then be used to surface more relevant search results, for example by weighting fridge ingredients higher on the assumption that the user is more actively trying to use them before they expire. Furthermor, it could be relevant to "use" a recipe, and the Fridge ingredients would get "used", while Pantry ingredients would remain. However, implementing this logic was considered out of scope for the current version of the project.

**`servings` in `recipes`**:
Not used in the current search or display logic beyond the recipe detail page, but included as it is a natural attribute of a recipe and would be the foundation for a future portion-scaling feature.

**`instructions` stored as JSON**:
Rather than normalising instructions into a separate table (e.g. a `steps` table with `recipe_id`, `step_number`, `text`), instructions are stored as a JSON array in the `recipes` table. This is justified because instructions are always retrieved and displayed as a complete ordered list — never queried individually — making a JSON column a simpler choice for this use case.

**`Tags`**:
Initially, the idea was for the user to be able to sort recipes by tags as well (e.g. European dishes, Desserts, Dishes <15 mins). However in the current version, the tags only figure as a detail about each dish when viewing a speicific recipe. 

## AI Declaration
An AI Declaration can be found in the repository.
