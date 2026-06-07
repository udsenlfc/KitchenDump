CREATE TABLE IF NOT EXISTS recipes (
    recipe_id    INT PRIMARY KEY,
    name         TEXT NOT NULL,
    cooking_time INT,
    servings     INT,
    description  TEXT,
    instructions JSON
);

CREATE TABLE IF NOT EXISTS ingredients (
    ingredient_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id      INT REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    ingredient_id  INT REFERENCES ingredients(ingredient_id) ON DELETE CASCADE,
    quantity       FLOAT,
    unit           TEXT,
    raw            TEXT,
    PRIMARY KEY (recipe_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS tags (
    tag_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS recipe_tags (
    recipe_id INT REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    tag_id INT REFERENCES tags(tag_id) ON DELETE CASCADE,
    PRIMARY KEY (recipe_id, tag_id)
);

CREATE TABLE IF NOT EXISTS storage (
    ingredient_id  INT REFERENCES ingredients(ingredient_id) ON DELETE CASCADE,
    category       TEXT CHECK (category IN ('pantry', 'fridge')),
    quantity       FLOAT,
    unit           TEXT,
    added_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ingredient_id, category)
);

CREATE TABLE IF NOT EXISTS favorites (
       recipe_id  INT REFERENCES recipes(recipe_id) ON DELETE CASCADE,
       saved_at   TIMESTAMP DEFAULT NOW(),
       PRIMARY KEY (recipe_id)
);