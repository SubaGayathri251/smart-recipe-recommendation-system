from flask import Flask, render_template, request

from recommendation_engine import (
    connect_database,
    load_recipe_data,
    recommend_recipes
)

from ml_model import load_model


# ============================================================
# CREATE FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# LOAD ML MODEL
# ============================================================

try:

    ml_model = load_model()

    print("ML model loaded successfully!")

except Exception as error:

    print("ML model loading failed:")
    print(error)

    ml_model = None


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# RECOMMEND RECIPES
# ============================================================

@app.route("/recommend", methods=["POST"])
def recommend():

    # --------------------------------------------------------
    # CHECK ML MODEL
    # --------------------------------------------------------

    if ml_model is None:

        return render_template(
            "index.html",
            error="ML model could not be loaded."
        )


    # --------------------------------------------------------
    # GET INGREDIENTS
    # --------------------------------------------------------

    ingredients_input = request.form.get(
        "ingredients",
        ""
    ).strip()


    if not ingredients_input:

        return render_template(
            "index.html",
            error="Please enter at least one ingredient."
        )


    # Convert ingredients into a list

    user_ingredients = [

        ingredient.strip().lower()

        for ingredient in ingredients_input.split(",")

        if ingredient.strip()

    ]


    # --------------------------------------------------------
    # GET CUISINE
    # --------------------------------------------------------

    cuisine = request.form.get(
        "cuisine",
        ""
    ).strip()


    if cuisine == "" or cuisine.lower() == "any":

        cuisine = None


    # --------------------------------------------------------
    # GET MEAL TYPE
    # --------------------------------------------------------

    meal_type = request.form.get(
        "meal_type",
        ""
    ).strip()


    if meal_type == "" or meal_type.lower() == "any":

        meal_type = None


    # --------------------------------------------------------
    # GET DIET TYPE
    # --------------------------------------------------------

    diet_type = request.form.get(
        "diet_type",
        ""
    ).strip()


    if diet_type == "" or diet_type.lower() == "any":

        diet_type = None


    # --------------------------------------------------------
    # GET MAXIMUM COOKING TIME
    # --------------------------------------------------------

    max_time_input = request.form.get(
        "max_time",
        ""
    ).strip()


    if max_time_input:

        try:

            max_time = int(max_time_input)

        except ValueError:

            max_time = None

    else:

        max_time = None


    # --------------------------------------------------------
    # GET MAXIMUM CALORIES
    # --------------------------------------------------------

    max_calories_input = request.form.get(
        "max_calories",
        ""
    ).strip()


    if max_calories_input:

        try:

            max_calories = float(
                max_calories_input
            )

        except ValueError:

            max_calories = None

    else:

        max_calories = None


    # --------------------------------------------------------
    # GET MINIMUM PROTEIN
    # --------------------------------------------------------

    min_protein_input = request.form.get(
        "min_protein",
        ""
    ).strip()


    if min_protein_input:

        try:

            min_protein = float(
                min_protein_input
            )

        except ValueError:

            min_protein = None

    else:

        min_protein = None


    # ========================================================
    # CONNECT TO MYSQL
    # ========================================================

    connection = connect_database()


    if connection is None:

        return render_template(
            "index.html",
            error="Could not connect to MySQL database."
        )


    try:

        # ----------------------------------------------------
        # LOAD ONLY CANDIDATE RECIPES
        # ----------------------------------------------------

        recipes = load_recipe_data(

    connection=connection,

    user_ingredients=user_ingredients,

    cuisine=cuisine,

    meal_type=meal_type,

    diet_type=diet_type,

    limit=5000

)
        


        # ----------------------------------------------------
        # CHECK IF RECIPES EXIST
        # ----------------------------------------------------

        if not recipes:

            return render_template(

                "index.html",

                error="No recipes found with the entered ingredients."

            )


        # ----------------------------------------------------
        # GENERATE RECOMMENDATIONS
        # ----------------------------------------------------

        recommendations = recommend_recipes(

            recipes=recipes,

            user_ingredients=user_ingredients,

            ml_model=ml_model,

            cuisine=cuisine,

            meal_type=meal_type,

            diet_type=diet_type,

            max_time=max_time,

            max_calories=max_calories,

            min_protein=min_protein,

            top_n=10

        )


        # ----------------------------------------------------
        # SHOW RESULTS
        # ----------------------------------------------------

        return render_template(

            "recommendations.html",

            recommendations=recommendations,

            search_ingredients=ingredients_input,

            cuisine=cuisine,

            meal_type=meal_type,

            diet_type=diet_type

        )


    except Exception as error:

        print("\nRecommendation error:")
        print(error)

        return render_template(

            "index.html",

            error="Something went wrong: " + str(error)

        )


    finally:

        if connection is not None:

            connection.close()

            print("Database connection closed.")


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )