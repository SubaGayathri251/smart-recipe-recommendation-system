import pandas as pd
import mysql.connector
from getpass import getpass
import re


# ============================================================
# CONFIGURATION
# ============================================================

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_NAME = "recipe_recommendation"

RECIPES_FILE = "data/processed/recipes_clean.csv"

BATCH_SIZE = 5000


# ============================================================
# SAFE INGREDIENT NORMALIZATION
# ============================================================

def normalize_ingredient(ingredient):
    """
    Safely normalizes an ingredient name.

    Examples:

        "Tomatoes"            -> "tomato"
        " tomatoes "          -> "tomato"
        "Chopped onion"       -> "onion"
        "Fresh potatoes"      -> "potato"
        "2 tomatoes"          -> "tomato"

    We do NOT blindly remove 's' or 'es' from every word.
    """

    # --------------------------------------------------------
    # 1. Handle missing values
    # --------------------------------------------------------

    if pd.isna(ingredient):
        return None

    ingredient = str(ingredient).strip().lower()

    if ingredient == "":
        return None

    # --------------------------------------------------------
    # 2. Remove extra spaces
    # --------------------------------------------------------

    ingredient = re.sub(r"\s+", " ", ingredient)

    # --------------------------------------------------------
    # 3. Remove quantities from beginning
    # --------------------------------------------------------

    # Examples:
    # 2 tomatoes
    # 3 onions
    # 1/2 cup milk
    # 2-3 potatoes

    ingredient = re.sub(
        r"^\s*\d+(?:\s*[-/]\s*\d+)?\s*",
        "",
        ingredient
    )

    # Remove fractions such as 1/2
    ingredient = re.sub(
        r"^\s*\d+\s*/\s*\d+\s*",
        "",
        ingredient
    )

    # --------------------------------------------------------
    # 4. Remove common preparation words
    # --------------------------------------------------------

    preparation_words = {
        "chopped",
        "diced",
        "sliced",
        "minced",
        "grated",
        "shredded",
        "crushed",
        "ground",
        "fresh",
        "frozen",
        "boiled",
        "cooked",
        "roasted",
        "fried",
        "peeled",
        "mashed"
    }

    words = ingredient.split()

    while words and words[0] in preparation_words:
        words.pop(0)

    ingredient = " ".join(words)

    if ingredient == "":
        return None

    # --------------------------------------------------------
    # 5. Remove trailing preparation descriptions
    # --------------------------------------------------------

    # Example:
    # "onion chopped" -> "onion"
    # "potatoes diced" -> "potatoes"

    trailing_words = {
        "chopped",
        "diced",
        "sliced",
        "minced",
        "grated",
        "shredded",
        "crushed",
        "peeled"
    }

    words = ingredient.split()

    while words and words[-1] in trailing_words:
        words.pop()

    ingredient = " ".join(words)

    if ingredient == "":
        return None

    # --------------------------------------------------------
    # 6. Remove unnecessary punctuation
    # --------------------------------------------------------

    ingredient = re.sub(
        r"^[,;:.]+|[,;:.]+$",
        "",
        ingredient
    )

    ingredient = ingredient.strip()

    # --------------------------------------------------------
    # 7. Explicit safe plural conversions
    # --------------------------------------------------------

    replacements = {

        # Vegetables
        "tomatoes": "tomato",
        "potatoes": "potato",
        "onions": "onion",
        "carrots": "carrot",
        "peppers": "pepper",
        "mushrooms": "mushroom",
        "peas": "pea",

        # Fruits
        "apples": "apple",
        "bananas": "banana",
        "lemons": "lemon",
        "limes": "lime",
        "oranges": "orange",

        # Dairy / eggs
        "eggs": "egg",

        # Spices
        "chilies": "chili",
        "chillies": "chili",

        # Other
        "beans": "bean",
        "nuts": "nut"
    }

    if ingredient in replacements:
        ingredient = replacements[ingredient]

    # --------------------------------------------------------
    # 8. Normalize some common equivalent names
    # --------------------------------------------------------

    equivalent_names = {

        "bell pepper": "bell pepper",
        "capsicum": "bell pepper",

        "green chilli": "green chili",
        "green chillies": "green chili",

        "red chilli": "red chili",
        "red chillies": "red chili",

        "coriander leaves": "coriander",
        "cilantro": "coriander",

        "spring onions": "spring onion",
        "scallions": "spring onion",

        "garbanzo beans": "chickpeas",
        "garbanzo bean": "chickpea",

        "chick peas": "chickpeas"
    }

    if ingredient in equivalent_names:
        ingredient = equivalent_names[ingredient]

    # --------------------------------------------------------
    # 9. Final cleanup
    # --------------------------------------------------------

    ingredient = re.sub(r"\s+", " ", ingredient)

    ingredient = ingredient.strip()

    if len(ingredient) < 2:
        return None

    return ingredient


# ============================================================
# START
# ============================================================

print("=" * 70)
print("SAFE INGREDIENT NORMALIZATION")
print("=" * 70)


# ============================================================
# MYSQL CONNECTION
# ============================================================

password = getpass("Enter your MySQL password: ")

try:

    connection = mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=password,
        database=DB_NAME
    )

    cursor = connection.cursor()

    print("\nMySQL connection successful!")

except mysql.connector.Error as e:

    print("\nMySQL connection failed.")
    print("Error:", e)

    exit()


# ============================================================
# LOAD RECIPE DATA
# ============================================================

print("\nLoading recipes...")

recipes = pd.read_csv(
    RECIPES_FILE,
    usecols=[
        "recipe_id",
        "ingredients_text"
    ],
    low_memory=False
)

print(
    f"Recipes loaded: {len(recipes):,}"
)


# ============================================================
# EXTRACT AND NORMALIZE INGREDIENTS
# ============================================================

print("\nNormalizing ingredients...")

unique_ingredients = set()

recipe_ingredient_map = {}

for index, row in recipes.iterrows():

    recipe_id = int(row["recipe_id"])

    ingredients_text = row["ingredients_text"]

    if pd.isna(ingredients_text):
        continue

    raw_ingredients = str(
        ingredients_text
    ).split(",")

    normalized_ingredients = set()

    for raw_ingredient in raw_ingredients:

        ingredient = normalize_ingredient(
            raw_ingredient
        )

        if ingredient:

            unique_ingredients.add(
                ingredient
            )

            normalized_ingredients.add(
                ingredient
            )

    recipe_ingredient_map[
        recipe_id
    ] = normalized_ingredients


print(
    f"Unique normalized ingredients: "
    f"{len(unique_ingredients):,}"
)


# ============================================================
# SHOW SAMPLE NORMALIZATION
# ============================================================

print("\nSample normalized ingredients:")

sample = sorted(unique_ingredients)[:30]

for ingredient in sample:
    print("  -", ingredient)


# ============================================================
# INSERT UNIQUE INGREDIENTS
# ============================================================

print("\nInserting ingredients into MySQL...")

insert_ingredient_sql = """
INSERT IGNORE INTO ingredients
(
    ingredient_name
)
VALUES (%s)
"""

ingredient_data = [
    (ingredient,)
    for ingredient in sorted(unique_ingredients)
]


for start in range(
    0,
    len(ingredient_data),
    BATCH_SIZE
):

    batch = ingredient_data[
        start:start + BATCH_SIZE
    ]

    cursor.executemany(
        insert_ingredient_sql,
        batch
    )

    connection.commit()

    processed = min(
        start + BATCH_SIZE,
        len(ingredient_data)
    )

    print(
        f"Ingredients inserted: "
        f"{processed:,}/"
        f"{len(ingredient_data):,}"
    )


# ============================================================
# GET MYSQL INGREDIENT IDs
# ============================================================

print("\nReading ingredient IDs from MySQL...")

cursor.execute("""
    SELECT
        ingredient_id,
        ingredient_name
    FROM ingredients
""")

rows = cursor.fetchall()

ingredient_id_map = {
    name: ingredient_id
    for ingredient_id, name in rows
}

print(
    f"Ingredient IDs loaded: "
    f"{len(ingredient_id_map):,}"
)


# ============================================================
# CREATE RECIPE-INGREDIENT RELATIONSHIPS
# ============================================================

print("\nCreating recipe-ingredient relationships...")

insert_relationship_sql = """
INSERT IGNORE INTO recipe_ingredients
(
    recipe_id,
    ingredient_id
)
VALUES (%s, %s)
"""

relationship_batch = []

total_recipes = len(recipe_ingredient_map)

processed_recipes = 0

total_relationships = 0


for recipe_id, ingredients in recipe_ingredient_map.items():

    for ingredient in ingredients:

        ingredient_id = ingredient_id_map.get(
            ingredient
        )

        if ingredient_id is None:
            continue

        relationship_batch.append(
            (
                recipe_id,
                ingredient_id
            )
        )

    processed_recipes += 1

    # --------------------------------------------------------
    # Batch insert
    # --------------------------------------------------------

    if len(relationship_batch) >= BATCH_SIZE:

        cursor.executemany(
            insert_relationship_sql,
            relationship_batch
        )

        connection.commit()

        total_relationships += len(
            relationship_batch
        )

        relationship_batch = []

        print(
            f"Recipes processed: "
            f"{processed_recipes:,}/"
            f"{total_recipes:,}"
            f" | Relationships: "
            f"{total_relationships:,}"
        )


# ============================================================
# INSERT REMAINING RELATIONSHIPS
# ============================================================

if relationship_batch:

    cursor.executemany(
        insert_relationship_sql,
        relationship_batch
    )

    connection.commit()

    total_relationships += len(
        relationship_batch
    )


# ============================================================
# CLOSE CONNECTION
# ============================================================

cursor.close()

connection.close()


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 70)
print("INGREDIENT PROCESSING COMPLETED SUCCESSFULLY!")
print("=" * 70)

print(
    f"\nRecipes processed       : "
    f"{total_recipes:,}"
)

print(
    f"Unique ingredients     : "
    f"{len(unique_ingredients):,}"
)

print(
    f"Relationships created  : "
    f"{total_relationships:,}"
)

print("\nMySQL tables populated:")

print("  ✓ ingredients")
print("  ✓ recipe_ingredients")