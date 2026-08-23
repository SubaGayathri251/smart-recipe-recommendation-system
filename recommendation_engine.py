import mysql.connector

from config import DB_CONFIG
from ml_model import load_model, predict_score


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_NAME = "recipe_recommendation"


# ============================================================
# CONNECT TO MYSQL
# ============================================================

import mysql.connector
from config import DB_CONFIG


def connect_database():

    try:

        connection = mysql.connector.connect(

            host=DB_CONFIG["host"],

            user=DB_CONFIG["user"],

            password=DB_CONFIG["password"],

            database=DB_CONFIG["database"],

            port=DB_CONFIG["port"]

        )

        print("MySQL database connected successfully!")

        return connection


    except mysql.connector.Error as error:

        print("Database connection failed:")
        print("Error:", error)

        return None


# ============================================================
# LOAD ALL RECIPES AND INGREDIENTS
# ============================================================

def load_recipe_data(

    connection,

    user_ingredients,

    cuisine=None,

    meal_type=None,

    diet_type=None,

    limit=5000

):

    cursor = connection.cursor(dictionary=True)


    conditions = []

    values = []


    # ========================================================
    # INGREDIENT FILTER
    # ========================================================

    ingredient_conditions = []


    for ingredient in user_ingredients:

        ingredient = normalize_ingredient(
            ingredient
        )


        ingredient_conditions.append(

            "LOWER(ingredients_text) LIKE %s"

        )


        values.append(

            f"%{ingredient.lower()}%"

        )


    if ingredient_conditions:

        conditions.append(

            "(" +
            " OR ".join(ingredient_conditions) +
            ")"

        )


    # ========================================================
    # CUISINE FILTER
    # ========================================================

    if cuisine:

        conditions.append(

            "LOWER(cuisine) = LOWER(%s)"

        )

        values.append(
            cuisine
        )


    # ========================================================
    # MEAL TYPE FILTER
    # ========================================================

    if meal_type:

        conditions.append(

            "LOWER(meal_type) = LOWER(%s)"

        )

        values.append(
            meal_type
        )


    # ========================================================
    # DIET TYPE FILTER
    # ========================================================

    if diet_type:

        conditions.append(

            "LOWER(diet_type) LIKE LOWER(%s)"

        )

        values.append(

            f"%{diet_type}%"

        )


    # ========================================================
    # SQL QUERY
    # ========================================================

    query = """

        SELECT

            recipe_id,

            recipe_name,

            instructions,

            total_time,

            n_steps,

            n_ingredients,

            difficulty,

            cuisine,

            meal_type,

            diet_type,

            calories,

            protein,

            carbohydrates,

            average_rating,

            rating_count,

            ingredients_text AS ingredients


        FROM recipes

    """


    if conditions:

        query += (

            " WHERE " +

            " AND ".join(
                conditions
            )

        )


    query += """

        ORDER BY average_rating DESC

        LIMIT %s

    """


    values.append(
        limit
    )


    print(

        "\nLoading filtered candidate recipes from MySQL..."

    )


    cursor.execute(

        query,

        values

    )


    recipes = cursor.fetchall()


    cursor.close()


    print(

        f"Candidate recipes loaded: {len(recipes):,}"

    )


    return recipes      


# ============================================================
# NORMALIZE INGREDIENT
# ============================================================

def normalize_ingredient(ingredient):

    ingredient = str(ingredient).strip().lower()

    # Common ingredient normalization
    replacements = {

        "tomatoes": "tomato",
        "potatoes": "potato",
        "onions": "onion",
        "carrots": "carrot",
        "eggs": "egg",
        "mushrooms": "mushroom",

        "peppers": "pepper",

        "chilies": "chili",
        "chillies": "chili",
        "chiles": "chili",

        "bananas": "banana",
        "apples": "apple",
        "lemons": "lemon",

        "cloves": "clove",

        "black peppercorns":
            "black peppercorn",

        "cilantro leaves":
            "cilantro",

        "chicken fillets":
            "chicken fillet"
    }

    if ingredient in replacements:

        ingredient = replacements[ingredient]

    return ingredient


# ============================================================
# NORMALIZE USER INGREDIENTS
# ============================================================

def normalize_user_ingredients(ingredients):

    normalized = set()

    for ingredient in ingredients:

        ingredient = normalize_ingredient(
            ingredient
        )

        if ingredient:

            normalized.add(
                ingredient
            )

    return normalized


# ============================================================
# INGREDIENT MATCHING
# ============================================================

def calculate_ingredient_score(
    user_ingredients,
    recipe_ingredients
):

    if not recipe_ingredients:

        return 0, set()

    matched = (
        user_ingredients
        .intersection(recipe_ingredients)
    )

    score = (
        len(matched)
        / len(recipe_ingredients)
    ) * 100

    return score, matched


# ============================================================
# CUISINE MATCH
# ============================================================

def calculate_cuisine_score(
    user_cuisine,
    recipe_cuisine
):

    if not user_cuisine:

        return 50

    if not recipe_cuisine:

        return 0

    recipe_cuisine = str(
        recipe_cuisine
    ).lower().strip()

    if recipe_cuisine == "unknown":

        return 0

    if (
        user_cuisine.lower().strip()
        == recipe_cuisine
    ):

        return 100

    return 0


# ============================================================
# MEAL TYPE MATCH
# ============================================================

def calculate_meal_score(
    user_meal,
    recipe_meal
):

    if not user_meal:

        return 50

    if not recipe_meal:

        return 0

    recipe_meal = str(
        recipe_meal
    ).lower().strip()

    if recipe_meal == "unknown":

        return 0

    if (
        user_meal.lower().strip()
        == recipe_meal
    ):

        return 100

    return 0


# ============================================================
# DIET MATCH
# ============================================================

def calculate_diet_score(
    user_diet,
    recipe_diet
):

    if not user_diet:

        return 50

    if not recipe_diet:

        return 0

    recipe_diet = str(
        recipe_diet
    ).lower().strip()

    if recipe_diet == "unknown":

        return 0

    if (
        user_diet.lower().strip()
        in recipe_diet
    ):

        return 100

    return 0


# ============================================================
# COOKING TIME MATCH
# ============================================================

def calculate_time_score(
    max_time,
    recipe_time
):

    if max_time is None:

        return 50

    if recipe_time is None:

        return 0

    try:

        recipe_time = float(
            recipe_time
        )

    except (ValueError, TypeError):

        return 0

    if recipe_time <= max_time:

        return 100

    difference = (
        recipe_time - max_time
    )

    score = 100 - (
        difference * 3
    )

    return max(0, score)


# ============================================================
# CALORIE MATCH
# ============================================================

def calculate_calorie_score(
    max_calories,
    recipe_calories
):

    if max_calories is None:

        return 50

    if recipe_calories is None:

        return 0

    try:

        recipe_calories = float(
            recipe_calories
        )

    except (ValueError, TypeError):

        return 0

    if recipe_calories <= max_calories:

        return 100

    difference = (
        recipe_calories - max_calories
    )

    score = 100 - (
        difference * 0.2
    )

    return max(0, score)


# ============================================================
# PROTEIN MATCH
# ============================================================

def calculate_protein_score(
    min_protein,
    recipe_protein
):

    if min_protein is None:

        return 50

    if recipe_protein is None:

        return 0

    try:

        recipe_protein = float(
            recipe_protein
        )

    except (ValueError, TypeError):

        return 0

    if recipe_protein >= min_protein:

        return 100

    difference = (
        min_protein - recipe_protein
    )

    score = 100 - (
        difference * 3
    )

    return max(0, score)


# ============================================================
# RATING SCORE
# ============================================================

def calculate_rating_score(rating):

    if rating is None:

        return 0

    try:

        rating = float(rating)

    except (ValueError, TypeError):

        return 0

    return (
        rating / 5
    ) * 100


# ============================================================
# RULE-BASED RECOMMENDATION SCORE
# ============================================================

def calculate_final_score(
    ingredient_score,
    cuisine_score,
    diet_score,
    meal_score,
    time_score,
    calorie_score,
    protein_score,
    rating_score
):

    score = (

        ingredient_score * 0.40

        + cuisine_score * 0.15

        + diet_score * 0.10

        + meal_score * 0.10

        + time_score * 0.08

        + calorie_score * 0.05

        + protein_score * 0.05

        + rating_score * 0.07
    )

    return round(
        score,
        2
    )
import re


# ============================================================
# FORMAT INSTRUCTIONS INTO COOKING STEPS
# ============================================================

def format_instructions(instructions):

    if not instructions:

        return []

    instructions = str(instructions).strip()

    # Convert multiple spaces into one space
    instructions = re.sub(
        r"\s+",
        " ",
        instructions
    )

    # Common cooking action words
    action_words = [

        "boil",
        "drain",
        "fry",
        "add",
        "mix",
        "stir",
        "cook",
        "bake",
        "heat",
        "preheat",
        "serve",
        "refrigerate",
        "chop",
        "slice",
        "cut",
        "wash",
        "soak",
        "grind",
        "blend",
        "pour",
        "place",
        "remove",
        "cover",
        "reduce",
        "bring",
        "turn",
        "sprinkle",
        "garnish",
        "combine",
        "whisk",
        "beat",
        "melt",
        "saute",
        "sauté",
        "roast",
        "steam"
    ]

    # Create regex pattern
    pattern = (
        r"(?=(" +
        "|".join(
            r"\b" + word + r"\b"
            for word in action_words
        ) +
        r"))"
    )

    # Split instructions before action words
    raw_steps = re.split(
        pattern,
        instructions,
        flags=re.IGNORECASE
    )

    formatted_steps = []

    for step in raw_steps:

        step = step.strip(
            " ,.-"
        )

        # Ignore very small fragments
        if len(step) > 10:

            # Capitalize first letter
            step = (
                step[0].upper()
                + step[1:]
            )

            formatted_steps.append(
                step
            )

    return formatted_steps


# ============================================================
# HYBRID RECOMMENDATION
# ============================================================

def recommend_recipes(
    recipes,
    user_ingredients,
    ml_model,
    cuisine=None,
    meal_type=None,
    diet_type=None,
    max_time=None,
    max_calories=None,
    min_protein=None,
    top_n=10
):

    recommendations = []

    # --------------------------------------------------------
    # Normalize user ingredients
    # --------------------------------------------------------

    user_ingredients = (
        normalize_user_ingredients(
            user_ingredients
        )
    )

    # --------------------------------------------------------
    # Process every recipe
    # --------------------------------------------------------

    for recipe in recipes:

        # ----------------------------------------------------
        # Recipe ingredients
        # ----------------------------------------------------

        ingredients_text = (
            recipe["ingredients"]
        )

        if ingredients_text:

            recipe_ingredients = {
                normalize_ingredient(
                    ingredient
                )
                for ingredient
                in ingredients_text.split(",")
                if ingredient.strip()
            }

        else:

            recipe_ingredients = set()

        # ----------------------------------------------------
        # Ingredient score
        # ----------------------------------------------------

        ingredient_score, matched = (
            calculate_ingredient_score(
                user_ingredients,
                recipe_ingredients
            )
        )

        # ----------------------------------------------------
        # Skip recipes with zero match
        # ----------------------------------------------------

        if ingredient_score == 0:

            continue

        # ----------------------------------------------------
        # Other scores
        # ----------------------------------------------------

        cuisine_score = (
            calculate_cuisine_score(
                cuisine,
                recipe["cuisine"]
            )
        )

        diet_score = (
            calculate_diet_score(
                diet_type,
                recipe["diet_type"]
            )
        )

        meal_score = (
            calculate_meal_score(
                meal_type,
                recipe["meal_type"]
            )
        )

        time_score = (
            calculate_time_score(
                max_time,
                recipe["total_time"]
            )
        )

        calorie_score = (
            calculate_calorie_score(
                max_calories,
                recipe["calories"]
            )
        )

        protein_score = (
            calculate_protein_score(
                min_protein,
                recipe["protein"]
            )
        )

        rating_score = (
            calculate_rating_score(
                recipe["average_rating"]
            )
        )

        # ----------------------------------------------------
        # Rule-based score
        # ----------------------------------------------------

        final_score = calculate_final_score(

            ingredient_score,

            cuisine_score,

            diet_score,

            meal_score,

            time_score,

            calorie_score,

            protein_score,

            rating_score
        )

        # ----------------------------------------------------
        # ML score
        # ----------------------------------------------------

        ml_score = predict_score(

            model=ml_model,

            total_time=recipe["total_time"],

            n_steps=recipe.get(
                "n_steps",
                0
            ),

            n_ingredients=len(
                recipe_ingredients
            ),

            calories=recipe["calories"],

            protein=recipe["protein"],

            carbohydrates=recipe["carbohydrates"],

            average_rating=recipe["average_rating"],

            rating_count=recipe["rating_count"]
        )

        # ----------------------------------------------------
        # HYBRID SCORE
        # ----------------------------------------------------

        hybrid_score = (

            final_score * 0.60

            + ml_score * 0.40

        )

        hybrid_score = round(
            hybrid_score,
            2
        )

        # ----------------------------------------------------
        # Missing ingredients
        # ----------------------------------------------------

        missing_ingredients = (
            recipe_ingredients
            - user_ingredients
        )

        # ----------------------------------------------------
        # Create result
        # ----------------------------------------------------

        result = {

    "recipe_id":
        recipe["recipe_id"],

    "recipe_name":
        recipe["recipe_name"],

    "instructions": format_instructions(
    recipe.get(
        "instructions",
        ""
    )
),

    "ingredients":
        recipe_ingredients,

    "matched_ingredients":
        matched,

    "missing_ingredients":
        missing_ingredients,

    "cuisine":
        recipe["cuisine"],

    "meal_type":
        recipe["meal_type"],

    "diet_type":
        recipe["diet_type"],

    "difficulty":
        recipe["difficulty"],

    "total_time":
        recipe["total_time"],

    "calories":
        recipe["calories"],

    "protein":
        recipe["protein"],

    "carbohydrates":
        recipe["carbohydrates"],

    "rating":
        recipe["average_rating"],

    "ingredient_score":
        round(
            ingredient_score,
            2
        ),

    "final_score":
        final_score,

    "ml_score":
        ml_score,

    "hybrid_score":
        hybrid_score
}

        recommendations.append(
            result
        )

    # --------------------------------------------------------
    # Sort by HYBRID SCORE
    # --------------------------------------------------------

    recommendations.sort(

        key=lambda recipe:
            recipe["hybrid_score"],

        reverse=True
    )

    return recommendations[:top_n]


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(
    recommendations
):

    print("\n")
    print("=" * 75)

    print(
        "              SMART RECIPE RECOMMENDATIONS"
    )

    print("=" * 75)

    if not recommendations:

        print(
            "\nNo matching recipes found."
        )

        return

    print(
        f"\nFound {len(recommendations)} "
        f"recommended recipe(s).\n"
    )

    for index, recipe in enumerate(
        recommendations,
        start=1
    ):

        print(
            f"\n{'=' * 75}"
        )

        print(
            f"#{index}  "
            f"{recipe['recipe_name']}"
        )

        print(
            f"{'=' * 75}"
        )

        print(
            f"Hybrid Recommendation Score : "
            f"{recipe['hybrid_score']}%"
        )

        print(
            f"Rule-Based Score             : "
            f"{recipe['final_score']}%"
        )

        print(
            f"ML Score                     : "
            f"{recipe['ml_score']}%"
        )

        print(
            f"Ingredient Match             : "
            f"{recipe['ingredient_score']}%"
        )

        print(
            f"Cuisine                      : "
            f"{recipe['cuisine']}"
        )

        print(
            f"Meal Type                    : "
            f"{recipe['meal_type']}"
        )

        print(
            f"Diet                         : "
            f"{recipe['diet_type']}"
        )

        print(
            f"Difficulty                   : "
            f"{recipe['difficulty']}"
        )

        print(
            f"Cooking Time                 : "
            f"{recipe['total_time']} minutes"
        )

        print(
            f"Calories                     : "
            f"{recipe['calories']}"
        )

        print(
            f"Protein                      : "
            f"{recipe['protein']} g"
        )

        print(
            f"Carbohydrates                : "
            f"{recipe['carbohydrates']} g"
        )

        print(
            f"Rating                       : "
            f"{recipe['rating']}"
        )

        # ----------------------------------------------------
        # Matched ingredients
        # ----------------------------------------------------

        print("\nYou already have:")

        if recipe["matched_ingredients"]:

            for ingredient in sorted(
                recipe["matched_ingredients"]
            ):

                print(
                    f"  ✓ {ingredient}"
                )

        else:

            print("  None")

        # ----------------------------------------------------
        # Missing ingredients
        # ----------------------------------------------------

        print("\nMissing ingredients:")

        if recipe["missing_ingredients"]:

            for ingredient in sorted(
                recipe["missing_ingredients"]
            ):

                print(
                    f"  ✗ {ingredient}"
                )

        else:

            print(
                "  None — you have everything!"
            )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 75)

    print(
        "       SMART RECIPE RECOMMENDATION SYSTEM"
    )

    print("=" * 75)

    # --------------------------------------------------------
    # Connect to MySQL
    # --------------------------------------------------------

    connection = connect_database()

    if connection is None:

        return

    # --------------------------------------------------------
    # Load ML model
    # --------------------------------------------------------

    try:

        ml_model = load_model()

        print(
            "Machine Learning model loaded successfully!"
        )

    except Exception as error:

        print(
            "\nFailed to load ML model."
        )

        print(
            "Error:",
            error
        )

        connection.close()

        return

    # --------------------------------------------------------
    # Load recipes
    # --------------------------------------------------------

    recipes = load_recipe_data(
        connection
    )

    # --------------------------------------------------------
    # User ingredients
    # --------------------------------------------------------

    ingredients_input = input(
        "\nEnter available ingredients "
        "(comma separated): "
    )

    user_ingredients = (
        ingredients_input.split(",")
    )

    # --------------------------------------------------------
    # Cuisine
    # --------------------------------------------------------

    cuisine = input(
        "Preferred cuisine "
        "(Indian/American/etc., Enter to skip): "
    ).strip()

    if cuisine == "":

        cuisine = None

    # --------------------------------------------------------
    # Meal
    # --------------------------------------------------------

    meal_type = input(
        "Meal type "
        "(Breakfast/Lunch/Dinner, Enter to skip): "
    ).strip()

    if meal_type == "":

        meal_type = None

    # --------------------------------------------------------
    # Diet
    # --------------------------------------------------------

    diet_type = input(
        "Diet type "
        "(Vegetarian/Non-Vegetarian, Enter to skip): "
    ).strip()

    if diet_type == "":

        diet_type = None

    # --------------------------------------------------------
    # Maximum cooking time
    # --------------------------------------------------------

    max_time_input = input(
        "Maximum cooking time in minutes "
        "(Enter to skip): "
    ).strip()

    if max_time_input:

        try:

            max_time = int(
                max_time_input
            )

        except ValueError:

            print(
                "Invalid cooking time."
            )

            max_time = None

    else:

        max_time = None

    # --------------------------------------------------------
    # Maximum calories
    # --------------------------------------------------------

    max_calories_input = input(
        "Maximum calories "
        "(Enter to skip): "
    ).strip()

    if max_calories_input:

        try:

            max_calories = float(
                max_calories_input
            )

        except ValueError:

            print(
                "Invalid calorie value."
            )

            max_calories = None

    else:

        max_calories = None

    # --------------------------------------------------------
    # Minimum protein
    # --------------------------------------------------------

    min_protein_input = input(
        "Minimum protein in grams "
        "(Enter to skip): "
    ).strip()

    if min_protein_input:

        try:

            min_protein = float(
                min_protein_input
            )

        except ValueError:

            print(
                "Invalid protein value."
            )

            min_protein = None

    else:

        min_protein = None

    # --------------------------------------------------------
    # Generate recommendations
    # --------------------------------------------------------

    print(
        "\nGenerating recommendations..."
    )

    recommendations = recommend_recipes(

        recipes,

        user_ingredients,

        ml_model,

        cuisine=cuisine,

        meal_type=meal_type,

        diet_type=diet_type,

        max_time=max_time,

        max_calories=max_calories,

        min_protein=min_protein,

        top_n=10
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    display_results(
        recommendations
    )

    # --------------------------------------------------------
    # Close database
    # --------------------------------------------------------

    connection.close()

    print(
        "\nDatabase connection closed."
    )

    print(
        "Recommendation process completed."
    )


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    main()