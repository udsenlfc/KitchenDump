from KitchenDump import db_cursor, conn

### Search for recipes based on your storage in the kitchen.
### Just press the "Use kitchen" button to get a list of recipes in order of how coverede they are.
def search_recipes_storage(ingredients):
    sql = """
        SELECT r.recipe_id, r.name, r.cooking_time,
            COUNT(DISTINCT CASE WHEN s.ingredient_id IS NOT NULL THEN ri.ingredient_id END) AS have_count,
            (SELECT COUNT(*) FROM recipe_ingredients
                WHERE recipe_id = r.recipe_id)
                - COUNT(DISTINCT CASE WHEN s.ingredient_id IS NOT NULL THEN ri.ingredient_id END) AS missing_count,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN s.ingredient_id IS NOT NULL THEN ri.ingredient_id END)
                    / (SELECT COUNT(*) FROM recipe_ingredients
                        WHERE recipe_id = r.recipe_id), 1) AS coverage_pct
        FROM recipes r
        JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
        JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
        LEFT JOIN storage s ON s.ingredient_id = ri.ingredient_id 
        GROUP BY r.recipe_id, r.name, r.cooking_time
        HAVING ROUND(100.0 * COUNT(DISTINCT CASE WHEN s.ingredient_id IS NOT NULL 
            THEN ri.ingredient_id END)
            / (SELECT COUNT(*) FROM recipe_ingredients
                WHERE recipe_id = r.recipe_id), 1) > 0
        ORDER BY coverage_pct DESC
        LIMIT 50
    """
    db_cursor.execute(sql, ([f"%{i}%" for i in ingredients],))
    return db_cursor.fetchall() if db_cursor.rowcount > 0 else []

### Search for recipes based on certain ingredients.
### Write the list of ingredients and press "Find recipes"
def search_recipes_ingredient(ingredients):
    sql = """
        SELECT r.recipe_id, r.name, r.cooking_time,
            COUNT(DISTINCT ri.ingredient_id) AS have_count,
            (SELECT COUNT(*) FROM recipe_ingredients
                WHERE recipe_id = r.recipe_id)
                - COUNT(DISTINCT ri.ingredient_id) AS missing_count,
            ROUND(100.0 * COUNT(DISTINCT ri.ingredient_id)
                    / (SELECT COUNT(*) FROM recipe_ingredients
                        WHERE recipe_id = r.recipe_id), 1) AS coverage_pct
        FROM recipes r
        JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
        JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
        WHERE i.name ILIKE ANY(%s)
        GROUP BY r.recipe_id, r.name, r.cooking_time
        HAVING COUNT(DISTINCT ri.ingredient_id) >= 1
        ORDER BY coverage_pct DESC
        LIMIT 50
    """
    db_cursor.execute(sql, ([f"%{i}%" for i in ingredients],))
    return db_cursor.fetchall() if db_cursor.rowcount > 0 else []

### Autocomplete ingredient search query.
### Used in My Kitchen when adding ingredients
### E.g. "Mi" shows "Milk"
def get_ingredient_suggestions(prefix):
    db_cursor.execute("""
        SELECT name FROM ingredients
        WHERE name ILIKE %s
          AND name NOT ILIKE '%%. %%'          
          AND name NOT SIMILAR TO '%%[0-9]%%'
          AND LENGTH(name) < 30
        ORDER BY name
        LIMIT 20
    """, (f"%{prefix}%",))
    results = db_cursor.fetchall()
    print(f"Autocomplete '{prefix}': {results}")
    return [row['name'] for row in results]

### Fetch the recipe page
def get_recipe_by_id(recipe_id):
    sql = """    
        SELECT recipe_id, name, cooking_time, servings, description, instructions
        FROM recipes
        WHERE recipe_id = %s
    """
    db_cursor.execute(sql, (recipe_id,))
    return db_cursor.fetchone()

### Fetch the list of ingredients in the recipe
def get_recipe_ingredients(recipe_id):
    sql = """
        SELECT i.name, ri.quantity, ri.unit, ri.raw
        FROM ingredients i
        JOIN recipe_ingredients ri ON i.ingredient_id = ri.ingredient_id
        WHERE ri.recipe_id = %s
        ORDER BY i.name
    """
    db_cursor.execute(sql, (recipe_id,))
    return db_cursor.fetchall() if db_cursor.rowcount > 0 else []

### Fetch all the tags of the recipe
def get_recipe_tags(recipe_id):
    sql = """
        SELECT t.name
        FROM tags t
        JOIN recipe_tags rt ON t.tag_id = rt.tag_id
        WHERE rt.recipe_id = %s
        ORDER BY t.name
    """
    db_cursor.execute(sql, (recipe_id,))
    return db_cursor.fetchall() if db_cursor.rowcount > 0 else []

### Fetches the ingredients currently in storage
def get_storage(category):
    sql = """
        SELECT i.name, s.quantity, s.unit, s.ingredient_id
        FROM ingredients i
        JOIN storage s ON i.ingredient_id = s.ingredient_id
        WHERE s.category = %s
        ORDER BY i.name
    """
    db_cursor.execute(sql, (category,))
    return db_cursor.fetchall() if db_cursor.rowcount > 0 else []

### Add ingredients to storage
def add_to_storage(ingredient_name, category):
    db_cursor.execute(
        "SELECT ingredient_id FROM ingredients WHERE name ILIKE %s",
        (ingredient_name,)
    )
    row = db_cursor.fetchone()
    if row:
        db_cursor.execute("""
            INSERT INTO storage (ingredient_id, category)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (row['ingredient_id'], category))
        conn.commit()
        return True
    return False

### Remove ingredients from storage
def remove_from_storage(ingredient_id, category):
    db_cursor.execute("""
        DELETE FROM storage
        WHERE ingredient_id = %s AND category = %s
    """, (ingredient_id, category))
    conn.commit()

### Returns all ingredient names in storage
### Used in search for recipes
def get_all_storage_names():
    db_cursor.execute("""
        SELECT i.name
        FROM ingredients i
        JOIN storage s ON i.ingredient_id = s.ingredient_id
    """)
    return [row['name'] for row in db_cursor.fetchall()]


### Add a recipe to list of favorite recipes
def insert_favorite(recipe_id):
    db_cursor.execute("""
        INSERT INTO favorites (recipe_id)
        VALUES (%s)
        ON CONFLICT DO NOTHING
    """, (recipe_id,))
    conn.commit()

### Get list of favorite recipes
def get_favorites():
    db_cursor.execute("""
        SELECT r.recipe_id, r.name
        FROM recipes r
        JOIN favorites f ON r.recipe_id = f.recipe_id
    """)
    return db_cursor.fetchall()

### Delete a recipe from list of favorites
def delete_favorite(recipe_id):
    db_cursor.execute("""
        DELETE FROM favorites 
        WHERE recipe_id = %s
    """, (recipe_id,))
    conn.commit()