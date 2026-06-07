import os
import json
import psycopg2

from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from choices import RecipeTagChoices, RecipeIngredientChoices, data

load_dotenv()

conn = psycopg2.connect(
    dbname=os.environ.get("DB_NAME", "kitchendump"),
    user=os.environ.get("DB_USER", "admin"),
    password=os.environ.get("DB_PASSWORD", "password"),
    host="127.0.0.1",
    port=5432
    )
cursor = conn.cursor(cursor_factory=RealDictCursor)

### Reads and executes "schema.sql" to initialise the tables in the database
schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
with open(schema_path, 'r') as f:
    cursor.execute(f.read())

### Inserts the recipes in the database.
for idx, recipe in enumerate(data):
    cursor.execute("""
        INSERT INTO recipes (recipe_id, name, cooking_time, servings, description, instructions)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (recipe_id) DO NOTHING
    """, (idx, recipe['title'], recipe['cooking_time'],
          recipe['servings'], recipe['description'],
          json.dumps(recipe['instructions'])))

### Inserts ingredients in the database.
for name in RecipeIngredientChoices.labels():
    cursor.execute("""
        INSERT INTO ingredients (name) VALUES (%s)
        ON CONFLICT (name) DO NOTHING
    """, (name,))

### Inserts tags in the database
for name in RecipeTagChoices.labels():
    cursor.execute("""
        INSERT INTO tags (name) VALUES (%s)
        ON CONFLICT (name) DO NOTHING
    """, (name,))

### Inserts the ingredients into the database for the specific recipe. 
for idx, recipe in enumerate(data):
    for ingredient in (recipe['ingredients'] or []):
        cursor.execute(
            "SELECT ingredient_id FROM ingredients WHERE name = %s",
            (ingredient['name'],)
        )
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit, raw)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                idx,
                row['ingredient_id'],
                ingredient.get('quantity'),
                ingredient.get('unit'),
                ingredient.get('raw')
            ))

### Inserts the tags for the specific recipe into the database.
for idx, recipe in enumerate(data):
    for tag_name in (recipe['tags'] or []):
        cursor.execute(
            "SELECT tag_id FROM tags WHERE name = %s",
            (tag_name,)
        )
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                INSERT INTO recipe_tags (recipe_id, tag_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (idx, row['tag_id']))

conn.commit()