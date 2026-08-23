import pandas as pd
import mysql.connector
from getpass import getpass


# ============================================================
# CONFIGURATION
# ============================================================

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_NAME = "recipe_recommendation"

RECIPES_FILE = "data/processed/recipes_clean.csv"
INTERACTIONS_FILE = "data/processed/interactions_clean.csv"

BATCH_SIZE = 1000


# ============================================================
# DATABASE CONNECTION
# ============================================================

print("=" * 60)
print("RECIPE RECOMMENDATION - MYSQL DATA IMPORT")
print("=" * 60)

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
# 1. LOAD RECIPES CSV
# ============================================================

print("\nLoading recipes CSV...")

recipes = pd.read_csv(
    RECIPES_FILE,
    low_memory=False
)

print(f"Recipes found: {len(recipes):,}")


# ============================================================
# 2. INSERT RECIPES
# ============================================================

print("\nInserting recipes into MySQL...")

recipe_query = """
INSERT IGNORE INTO recipes (
    recipe_id,
    recipe_name,
    description,
    ingredients_text,
    instructions,
    total_time,
    n_steps,
    n_ingredients,
    difficulty,
    cuisine,
    meal_type,
    diet_type,
    spice_level,
    calories,
    total_fat,
    sugar,
    sodium,
    protein,
    saturated_fat,
    carbohydrates,
    average_rating,
    rating_count,
    tags_text,
    ml_text
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s
)
"""

recipe_columns = [
    "recipe_id",
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


def clean_value(value):

    if pd.isna(value):
        return None

    return value


recipe_batch = []

total_recipes = len(recipes)

for index, row in recipes.iterrows():

    values = tuple(
        clean_value(row[column])
        for column in recipe_columns
    )

    recipe_batch.append(values)

    if len(recipe_batch) >= BATCH_SIZE:

        cursor.executemany(
            recipe_query,
            recipe_batch
        )

        connection.commit()

        processed = index + 1

        print(
            f"Recipes imported: "
            f"{processed:,}/{total_recipes:,}"
        )

        recipe_batch = []


# Insert remaining recipes

if recipe_batch:

    cursor.executemany(
        recipe_query,
        recipe_batch
    )

    connection.commit()


print("\nRecipe import completed!")


# ============================================================
# 3. LOAD INTERACTIONS
# ============================================================

print("\nLoading interactions CSV...")

interactions = pd.read_csv(
    INTERACTIONS_FILE,
    low_memory=False
)

print(
    f"Interactions found: "
    f"{len(interactions):,}"
)


# ============================================================
# 4. INSERT USERS
# ============================================================

print("\nCreating users...")

users = interactions[
    ["user_id"]
].drop_duplicates()

user_query = """
INSERT IGNORE INTO users (
    user_id
)
VALUES (%s)
"""

user_batch = []

for index, row in users.iterrows():

    user_batch.append(
        (int(row["user_id"]),)
    )

    if len(user_batch) >= BATCH_SIZE:

        cursor.executemany(
            user_query,
            user_batch
        )

        connection.commit()

        user_batch = []

if user_batch:

    cursor.executemany(
        user_query,
        user_batch
    )

    connection.commit()


print(
    f"Users imported: "
    f"{len(users):,}"
)


# ============================================================
# 5. INSERT RATINGS
# ============================================================

print("\nInserting ratings and reviews...")

rating_query = """
INSERT IGNORE INTO ratings (
    user_id,
    recipe_id,
    rating,
    review,
    rating_date
)
VALUES (%s, %s, %s, %s, %s)
"""

rating_batch = []

total_interactions = len(interactions)

for index, row in interactions.iterrows():

    user_id = clean_value(row["user_id"])
    recipe_id = clean_value(row["recipe_id"])
    rating = clean_value(row["rating"])
    review = clean_value(row["review"])
    date = clean_value(row["date"])

    if user_id is None or recipe_id is None:
        continue

    values = (
        int(user_id),
        int(recipe_id),
        int(rating) if rating is not None else None,
        review,
        date
    )

    rating_batch.append(values)

    if len(rating_batch) >= BATCH_SIZE:

        cursor.executemany(
            rating_query,
            rating_batch
        )

        connection.commit()

        processed = index + 1

        print(
            f"Interactions imported: "
            f"{processed:,}/{total_interactions:,}"
        )

        rating_batch = []


# Remaining ratings

if rating_batch:

    cursor.executemany(
        rating_query,
        rating_batch
    )

    connection.commit()


print("\nRating import completed!")


# ============================================================
# 6. CLOSE CONNECTION
# ============================================================

cursor.close()
connection.close()

print("\n" + "=" * 60)
print("DATA IMPORT COMPLETED SUCCESSFULLY!")
print("=" * 60)