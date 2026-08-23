import ast
import re
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

RECIPES_FILE = RAW_DIR / "RAW_recipes.csv"
INTERACTIONS_FILE = RAW_DIR / "RAW_interactions.csv"


# ============================================================
# 2. HELPER FUNCTIONS
# ============================================================

def parse_list(value):
    """
    Convert a string representation of a Python list into
    an actual list.

    Example:
        "['tomato', 'onion']"
        ->
        ['tomato', 'onion']
    """

    if pd.isna(value):
        return []

    if isinstance(value, list):
        return value

    try:
        result = ast.literal_eval(value)

        if isinstance(result, list):
            return result

        return [str(result)]

    except (ValueError, SyntaxError):
        return [str(value)]


def clean_text(text):
    """
    Basic text cleaning.
    """

    if pd.isna(text):
        return ""

    text = str(text)

    text = text.lower()

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def clean_ingredient(ingredient):
    """
    Normalize ingredient names.
    """

    ingredient = clean_text(ingredient)

    # Remove excessive punctuation
    ingredient = re.sub(r"[^a-z0-9\s\-]", "", ingredient)

    # Normalize common plural forms
    replacements = {
        "tomatoes": "tomato",
        "onions": "onion",
        "potatoes": "potato",
        "carrots": "carrot",
        "eggs": "egg",
        "peppers": "pepper",
        "mushrooms": "mushroom",
        "lemons": "lemon",
        "limes": "lime",
        "apples": "apple",
        "bananas": "banana",
    }

    return replacements.get(ingredient, ingredient)


def clean_ingredient_list(ingredients):
    """
    Clean a list of ingredients and remove duplicates.
    """

    cleaned = []

    for ingredient in ingredients:

        ingredient = clean_ingredient(ingredient)

        if ingredient and ingredient not in cleaned:
            cleaned.append(ingredient)

    return cleaned


def parse_nutrition(value):
    """
    Food.com nutrition format:

    [calories, total_fat, sugar, sodium,
     protein, saturated_fat, carbohydrates]
    """

    values = parse_list(value)

    numbers = []

    for item in values:

        try:
            numbers.append(float(item))
        except (ValueError, TypeError):
            numbers.append(np.nan)

    while len(numbers) < 7:
        numbers.append(np.nan)

    return numbers[:7]


def infer_diet(tags):
    """
    Infer diet type cautiously from tags.
    """

    tag_string = " ".join(tags).lower()

    if "vegan" in tag_string:
        return "Vegan"

    if "vegetarian" in tag_string:
        return "Vegetarian"

    if "egg-free" in tag_string:
        return "Egg-Free"

    return "Unknown"


def infer_meal_type(tags):
    """
    Infer meal type from Food.com tags.
    """

    tag_string = " ".join(tags).lower()

    if "breakfast" in tag_string:
        return "Breakfast"

    if "lunch" in tag_string:
        return "Lunch"

    if "dinner" in tag_string:
        return "Dinner"

    if "dessert" in tag_string:
        return "Dessert"

    if "snacks" in tag_string or "snack" in tag_string:
        return "Snack"

    return "Unknown"


def infer_cuisine(tags):
    """
    Infer cuisine when an explicit cuisine-like tag exists.
    """

    tag_string = " ".join(tags).lower()

    cuisines = {
        "indian": "Indian",
        "italian": "Italian",
        "mexican": "Mexican",
        "chinese": "Chinese",
        "thai": "Thai",
        "japanese": "Japanese",
        "korean": "Korean",
        "french": "French",
        "greek": "Greek",
        "mediterranean": "Mediterranean",
        "american": "American",
    }

    for keyword, cuisine in cuisines.items():

        if keyword in tag_string:
            return cuisine

    return "Unknown"


def calculate_difficulty(minutes, n_steps, n_ingredients):

    if pd.isna(minutes):
        return "Unknown"

    score = 0

    # Cooking/preparation time
    if minutes > 60:
        score += 2
    elif minutes > 30:
        score += 1

    # Number of steps
    if n_steps > 12:
        score += 2
    elif n_steps > 7:
        score += 1

    # Number of ingredients
    if n_ingredients > 15:
        score += 2
    elif n_ingredients > 8:
        score += 1

    if score <= 1:
        return "Easy"

    elif score <= 3:
        return "Medium"

    return "Hard"


# ============================================================
# 3. LOAD DATA
# ============================================================

print("=" * 60)
print("Loading datasets...")
print("=" * 60)

recipes = pd.read_csv(RECIPES_FILE)

interactions = pd.read_csv(INTERACTIONS_FILE)

print(f"Recipes loaded: {len(recipes):,}")
print(f"Interactions loaded: {len(interactions):,}")


# ============================================================
# 4. KEEP ONLY REQUIRED RAW COLUMNS
# ============================================================

recipe_columns = [
    "name",
    "id",
    "minutes",
    "tags",
    "nutrition",
    "n_steps",
    "steps",
    "description",
    "ingredients",
    "n_ingredients"
]

recipes = recipes[recipe_columns].copy()

interaction_columns = [
    "user_id",
    "recipe_id",
    "date",
    "rating",
    "review"
]

interactions = interactions[interaction_columns].copy()


# ============================================================
# 5. REMOVE DUPLICATE RECIPES
# ============================================================

recipes.drop_duplicates(
    subset=["id"],
    inplace=True
)


# ============================================================
# 6. PARSE LIST COLUMNS
# ============================================================

print("\nParsing list columns...")

recipes["tags"] = recipes["tags"].apply(parse_list)

recipes["ingredients"] = recipes["ingredients"].apply(parse_list)

recipes["steps"] = recipes["steps"].apply(parse_list)


# ============================================================
# 7. CLEAN TEXT
# ============================================================

recipes["recipe_name"] = recipes["name"].apply(clean_text)

recipes["description"] = recipes["description"].apply(clean_text)


# ============================================================
# 8. CLEAN INGREDIENTS
# ============================================================

recipes["ingredients_clean"] = recipes["ingredients"].apply(
    clean_ingredient_list
)


# Convert ingredient list to a searchable string

recipes["ingredients_text"] = recipes["ingredients_clean"].apply(
    lambda x: ", ".join(x)
)


# ============================================================
# 9. CLEAN INSTRUCTIONS
# ============================================================

recipes["instructions"] = recipes["steps"].apply(
    lambda steps: " ".join(
        clean_text(step)
        for step in steps
    )
)


# ============================================================
# 10. CLEAN TAGS
# ============================================================

recipes["tags_text"] = recipes["tags"].apply(
    lambda tags: ", ".join(
        clean_text(tag)
        for tag in tags
    )
)


# ============================================================
# 11. EXTRACT NUTRITION
# ============================================================

print("\nExtracting nutrition information...")

nutrition_data = recipes["nutrition"].apply(parse_nutrition)

nutrition_df = pd.DataFrame(
    nutrition_data.tolist(),
    columns=[
        "calories",
        "total_fat",
        "sugar",
        "sodium",
        "protein",
        "saturated_fat",
        "carbohydrates"
    ],
    index=recipes.index
)

recipes = pd.concat(
    [recipes, nutrition_df],
    axis=1
)


# ============================================================
# 12. CALCULATE RATING INFORMATION
# ============================================================

print("\nCalculating recipe ratings...")

interactions["rating"] = pd.to_numeric(
    interactions["rating"],
    errors="coerce"
)

rating_summary = (
    interactions
    .groupby("recipe_id")["rating"]
    .agg(
        average_rating="mean",
        rating_count="count"
    )
    .reset_index()
)

recipes = recipes.merge(
    rating_summary,
    how="left",
    left_on="id",
    right_on="recipe_id"
)


recipes["average_rating"] = recipes[
    "average_rating"
].fillna(0)

recipes["rating_count"] = recipes[
    "rating_count"
].fillna(0)


# ============================================================
# 13. INFER DIET TYPE
# ============================================================

print("\nInferring diet types...")

recipes["diet_type"] = recipes["tags"].apply(
    infer_diet
)


# ============================================================
# 14. INFER MEAL TYPE
# ============================================================

print("Inferring meal types...")

recipes["meal_type"] = recipes["tags"].apply(
    infer_meal_type
)


# ============================================================
# 15. INFER CUISINE
# ============================================================

print("Inferring cuisines...")

recipes["cuisine"] = recipes["tags"].apply(
    infer_cuisine
)


# ============================================================
# 16. CREATE SPICE LEVEL
# ============================================================

def infer_spice(tags):

    tag_string = " ".join(tags).lower()

    spicy_words = [
        "spicy",
        "hot",
        "chili",
        "chilli",
        "pepper"
    ]

    if any(word in tag_string for word in spicy_words):
        return "Spicy"

    return "Unknown"


recipes["spice_level"] = recipes["tags"].apply(
    infer_spice
)


# ============================================================
# 17. CALCULATE DIFFICULTY
# ============================================================

print("Calculating difficulty...")

recipes["difficulty"] = recipes.apply(
    lambda row: calculate_difficulty(
        row["minutes"],
        row["n_steps"],
        row["n_ingredients"]
    ),
    axis=1
)


# ============================================================
# 18. CLEAN COOKING TIME
# ============================================================

recipes["minutes"] = pd.to_numeric(
    recipes["minutes"],
    errors="coerce"
)

recipes.rename(
    columns={
        "minutes": "total_time"
    },
    inplace=True
)


# ============================================================
# 19. REMOVE INVALID RECIPES
# ============================================================

print("\nRemoving invalid recipes...")

recipes = recipes[
    recipes["recipe_name"].notna()
]

recipes = recipes[
    recipes["recipe_name"] != ""
]

recipes = recipes[
    recipes["ingredients_text"].str.len() > 0
]

recipes = recipes[
    recipes["total_time"] >= 1
]

recipes = recipes[
    recipes["total_time"] <= 1440
]


# ============================================================
# 20. REMOVE EXTREME / INVALID NUTRITION VALUES
# ============================================================

recipes.loc[
    recipes["calories"] < 0,
    "calories"
] = np.nan

recipes.loc[
    recipes["protein"] < 0,
    "protein"
] = np.nan

recipes.loc[
    recipes["carbohydrates"] < 0,
    "carbohydrates"
] = np.nan

recipes.loc[
    recipes["total_fat"] < 0,
    "total_fat"
] = np.nan


# ============================================================
# 21. CREATE RECIPE TEXT FOR ML
# ============================================================

recipes["ml_text"] = (
    recipes["recipe_name"].fillna("")
    + " "
    + recipes["description"].fillna("")
    + " "
    + recipes["ingredients_text"].fillna("")
    + " "
    + recipes["tags_text"].fillna("")
)


# ============================================================
# 22. CREATE FINAL RECIPE DATAFRAME
# ============================================================

final_columns = [
    "id",
    "recipe_name",
    "description",
    "ingredients_text",
    "instructions",
    "total_time",
    "n_steps",
    "n_ingredients",
    "difficulty",
    "cuisine",
    "meal_type",
    "diet_type",
    "spice_level",
    "calories",
    "total_fat",
    "sugar",
    "sodium",
    "protein",
    "saturated_fat",
    "carbohydrates",
    "average_rating",
    "rating_count",
    "tags_text",
    "ml_text"
]

recipes_final = recipes[
    final_columns
].copy()


# ============================================================
# 23. RENAME RECIPE ID
# ============================================================

recipes_final.rename(
    columns={
        "id": "recipe_id"
    },
    inplace=True
)


# ============================================================
# 24. ROUND NUMERICAL VALUES
# ============================================================

numeric_columns = [
    "total_time",
    "calories",
    "total_fat",
    "sugar",
    "sodium",
    "protein",
    "saturated_fat",
    "carbohydrates",
    "average_rating"
]

for column in numeric_columns:

    recipes_final[column] = pd.to_numeric(
        recipes_final[column],
        errors="coerce"
    ).round(2)


# ============================================================
# 25. CLEAN INTERACTIONS
# ============================================================

interactions["rating"] = pd.to_numeric(
    interactions["rating"],
    errors="coerce"
)

interactions = interactions[
    interactions["rating"].between(1, 5)
]

interactions["date"] = pd.to_datetime(
    interactions["date"],
    errors="coerce"
)

interactions = interactions.dropna(
    subset=[
        "user_id",
        "recipe_id",
        "rating"
    ]
)


# ============================================================
# 26. KEEP ONLY INTERACTIONS FOR VALID RECIPES
# ============================================================

valid_recipe_ids = set(
    recipes_final["recipe_id"]
)

interactions = interactions[
    interactions["recipe_id"].isin(
        valid_recipe_ids
    )
]


# ============================================================
# 27. REMOVE DUPLICATE USER-RECIPE INTERACTIONS
# ============================================================

interactions = interactions.drop_duplicates(
    subset=[
        "user_id",
        "recipe_id"
    ],
    keep="last"
)


# ============================================================
# 28. SAVE CLEAN RECIPE DATASET
# ============================================================

recipes_output = (
    PROCESSED_DIR /
    "recipes_clean.csv"
)

recipes_final.to_csv(
    recipes_output,
    index=False
)


# ============================================================
# 29. SAVE CLEAN INTERACTIONS
# ============================================================

interactions_output = (
    PROCESSED_DIR /
    "interactions_clean.csv"
)

interactions.to_csv(
    interactions_output,
    index=False
)


# ============================================================
# 30. PRINT SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("PREPROCESSING COMPLETE")
print("=" * 60)

print(
    f"Final recipes: "
    f"{len(recipes_final):,}"
)

print(
    f"Final interactions: "
    f"{len(interactions):,}"
)

print(
    f"Unique users: "
    f"{interactions['user_id'].nunique():,}"
)

print(
    f"Average recipe rating: "
    f"{recipes_final['average_rating'].mean():.2f}"
)

print(
    f"Recipes with ratings: "
    f"{(recipes_final['rating_count'] > 0).sum():,}"
)

print("\nFiles created:")

print(recipes_output)

print(interactions_output)

print("\nSample recipe data:")

print(
    recipes_final[
        [
            "recipe_id",
            "recipe_name",
            "ingredients_text",
            "total_time",
            "calories",
            "protein",
            "average_rating"
        ]
    ].head()
)

print("\nDone!")