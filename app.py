from flask import Flask, render_template, request, jsonify, redirect, url_for
import KitchenDump.queries as q 

app = Flask(__name__)

### Flask for the index html page.
### Allowed methods "GET" and "POST"
### Renders the "index.html" file for the main page
### - "kitchen": searches for recipes using the current storage in the kitchen.
### - "ingredient": searches for recipes using ingredients typed in search bar.
@app.route("/", methods=["GET", "POST"])
def index():
    results_kitchen = []
    results_ingredient = []
    if request.method == "POST":
        action = request.form.get("action")
        raw = request.form.get("ingredients", "")
        ingredients = [i.strip() for i in raw.split(",") if i.strip()]
        if action == "kitchen":
            storage_ingredient = q.get_all_storage_names()
            all_ingredients = list(set(ingredients + storage_ingredient))
            results_kitchen = q.search_recipes_storage(all_ingredients)

        elif action == "ingredient":
            results_ingredient = q.search_recipes_ingredient(ingredients)

    favorites = q.get_favorites()
    return render_template("index.html", results_kitchen=results_kitchen, results_ingredient=results_ingredient, favorites=favorites)


### Flask for the recipes html pages.
### Allowed methods "GET" and "POST"
### Renders the "recipe.html" file for the unique recipe_id.
### - "add": adds the recipe to list of favorites.
### - "delete": deletes the recipe from list of favorites.
@app.route("/recipe/<int:recipe_id>", methods=["GET", "POST"])
def recipe(recipe_id):
    recipe = q.get_recipe_by_id(recipe_id)
    ingredients = q.get_recipe_ingredients(recipe_id)
    print(ingredients[:2])
    tags = q.get_recipe_tags(recipe_id)
    favorites = q.get_favorites()
    is_favorite = any(f['recipe_id'] == recipe_id for f in favorites)

    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add":
            fav_recipe_id = request.form.get("recipe_id")
            q.insert_favorite(fav_recipe_id)
            return redirect(url_for('recipe', recipe_id=recipe_id))

        elif action == "delete":
            fav_recipe_id = request.form.get("recipe_id")
            q.delete_favorite(fav_recipe_id)
            return redirect(url_for('recipe', recipe_id=recipe_id))

    favorites = q.get_favorites()

    return render_template("recipe.html", recipe=recipe,
                           ingredients=ingredients, tags=tags, favorites=favorites,
                           is_favorite=is_favorite)

### Flask for the autocomplete
@app.route("/autocomplete")
def autocomplete():
    prefix = request.args.get("q", "").strip()
    if len(prefix) < 2:
        return jsonify([])
    suggestions = q.get_ingredient_suggestions(prefix)
    return jsonify(suggestions)

### Flask for the storage html page.
### Allowed methods "GET" and "POST"
### Renders the "storage.html" file.
### - "add": adds an ingredient to either pantry or fridge.
### - "remove": removes an ingredient from the storage.
@app.route("/storage", methods=["GET", "POST"])
def storage():
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "add":
            name = request.form.get("ingredient_query", "").strip().lower()
            category = request.form.get("category", "pantry")
            q.add_to_storage(name, category)
        
        elif action == "remove":
            ingredient_id = request.form.get("ingredient_id")
            category = request.form.get("category")
            q.remove_from_storage(ingredient_id, category)
    pantry = q.get_storage("pantry")
    fridge = q.get_storage("fridge")
    return render_template("storage.html", pantry=pantry, fridge=fridge)

### Flask for the favorites html pages.
### Allowed methods "GET" and "POST"
### Renders the "favorites.html" file.
### - "delete": deletes the recipe from list of favorites.
@app.route("/favorites", methods=["GET", "POST"])
def favorites_page():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "delete":
            recipe_id = request.form.get("recipe_id")
            q.delete_favorite(recipe_id)


    favorites = q.get_favorites()

    return render_template("favorites.html", favorites=favorites)


if __name__ == "__main__":
    app.run(debug=True)
