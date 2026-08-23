import joblib
import pandas as pd
import os


# ============================================================
# MODEL LOCATION
# ============================================================

MODEL_FILE = os.path.join(
    "models",
    "recipe_recommendation_model.pkl"
)


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

def load_model():

    if not os.path.exists(MODEL_FILE):

        raise FileNotFoundError(
            "Trained ML model not found. "
            "Please run train_ml_model.py first."
        )

    model = joblib.load(
        MODEL_FILE
    )

    return model


# ============================================================
# PREDICT RECOMMENDATION SCORE
# ============================================================

def predict_score(
    model,
    total_time,
    n_steps,
    n_ingredients,
    calories,
    protein,
    carbohydrates,
    average_rating,
    rating_count
):

    data = pd.DataFrame([{

        "total_time": total_time,

        "n_steps": n_steps,

        "n_ingredients": n_ingredients,

        "calories": calories,

        "protein": protein,

        "carbohydrates": carbohydrates,

        "average_rating": average_rating,

        "rating_count": rating_count

    }])

    prediction = model.predict(data)[0]

    prediction = max(
        0,
        min(100, prediction)
    )

    return round(
        prediction,
        2
    )


# ============================================================
# TEST THE MODEL
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "       TESTING RECIPE ML MODEL"
    )

    print("=" * 60)

    model = load_model()

    print(
        "\nModel loaded successfully!"
    )

    score = predict_score(

        model=model,

        total_time=30,

        n_steps=8,

        n_ingredients=7,

        calories=400,

        protein=25,

        carbohydrates=30,

        average_rating=4.5,

        rating_count=100
    )

    print(
        f"\nPredicted Recommendation Score: "
        f"{score}%"
    )

    print(
        "\nML prediction completed."
    )