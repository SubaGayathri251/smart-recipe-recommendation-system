import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

import joblib
import os


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "data/processed/recipes_clean.csv"

MODEL_FOLDER = "models"

MODEL_FILE = os.path.join(
    MODEL_FOLDER,
    "recipe_recommendation_model.pkl"
)


# ============================================================
# CREATE MODEL DIRECTORY
# ============================================================

os.makedirs(
    MODEL_FOLDER,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("       TRAINING RECIPE RECOMMENDATION ML MODEL")
print("=" * 70)

print("\nLoading recipe dataset...")

df = pd.read_csv(
    DATA_FILE
)

print(
    f"Recipes loaded: {len(df):,}"
)


# ============================================================
# SELECT REQUIRED COLUMNS
# ============================================================

required_columns = [

    "total_time",
    "n_steps",
    "n_ingredients",
    "calories",
    "protein",
    "carbohydrates",
    "average_rating",
    "rating_count"
]


# Check whether columns exist

missing_columns = [

    column
    for column in required_columns
    if column not in df.columns
]


if missing_columns:

    print(
        "\nMissing columns:"
    )

    print(
        missing_columns
    )

    exit()


# ============================================================
# CLEAN NUMERIC DATA
# ============================================================

print(
    "\nCleaning numerical data..."
)


for column in required_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# Replace missing values

df[required_columns] = (
    df[required_columns]
    .fillna(0)
)


# ============================================================
# CREATE TARGET VARIABLE
# ============================================================

print(
    "\nCreating recommendation target..."
)


# Normalize rating from 0-5 to 0-100

rating_score = (
    df["average_rating"] / 5
) * 100


# Normalize ingredient count

ingredient_score = (
    100
    - (
        abs(
            df["n_ingredients"] - 6
        ) * 5
    )
)


ingredient_score = (
    ingredient_score
    .clip(0, 100)
)


# Cooking time score

time_score = np.where(

    df["total_time"] <= 30,

    100,

    np.maximum(
        0,
        100 -
        (
            df["total_time"] - 30
        ) * 2
    )
)


# Protein score

protein_score = np.minimum(

    df["protein"] * 3,

    100
)


# Final target

df["recommendation_score"] = (

    rating_score * 0.35

    + ingredient_score * 0.20

    + time_score * 0.20

    + protein_score * 0.25

)


# Keep score between 0 and 100

df["recommendation_score"] = (
    df["recommendation_score"]
    .clip(0, 100)
)


# ============================================================
# SELECT ML FEATURES
# ============================================================

features = [

    "total_time",
    "n_steps",
    "n_ingredients",
    "calories",
    "protein",
    "carbohydrates",
    "average_rating",
    "rating_count"
]


X = df[features]

y = df[
    "recommendation_score"
]


print(
    "\nFeatures used by the ML model:"
)

for feature in features:

    print(
        f"  ✓ {feature}"
    )


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

print(
    "\nSplitting dataset..."
)

X_train, X_test, y_train, y_test = (
    train_test_split(

        X,
        y,

        test_size=0.20,

        random_state=42
    )
)


print(
    f"Training samples: {len(X_train):,}"
)

print(
    f"Testing samples : {len(X_test):,}"
)


# ============================================================
# CREATE RANDOM FOREST
# ============================================================

print(
    "\nCreating Random Forest model..."
)


model = RandomForestRegressor(

    n_estimators=100,

    max_depth=15,

    random_state=42,

    n_jobs=-1
)


# ============================================================
# TRAIN
# ============================================================

print(
    "\nTraining model..."
)

model.fit(
    X_train,
    y_train
)


print(
    "Model training completed!"
)


# ============================================================
# PREDICTION
# ============================================================

print(
    "\nTesting model..."
)


predictions = model.predict(
    X_test
)


# ============================================================
# EVALUATION
# ============================================================

mae = mean_absolute_error(
    y_test,
    predictions
)

r2 = r2_score(
    y_test,
    predictions
)


print("\n")
print("=" * 70)

print(
    "MODEL PERFORMANCE"
)

print("=" * 70)

print(
    f"Mean Absolute Error : {mae:.2f}"
)

print(
    f"R² Score            : {r2:.2f}"
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print("\n")
print(
    "FEATURE IMPORTANCE"
)

print("=" * 70)


importance = pd.DataFrame({

    "feature": features,

    "importance":
        model.feature_importances_

})


importance = (
    importance
    .sort_values(
        "importance",
        ascending=False
    )
)


for _, row in importance.iterrows():

    print(
        f"{row['feature']:20s} "
        f"{row['importance']:.4f}"
    )


# ============================================================
# SAVE MODEL
# ============================================================

print(
    "\nSaving trained model..."
)


joblib.dump(

    model,

    MODEL_FILE
)


print(
    f"\nModel saved successfully:"
)

print(
    MODEL_FILE
)


# ============================================================
# COMPLETE
# ============================================================

print("\n")
print("=" * 70)

print(
    "ML MODEL TRAINING COMPLETED"
)

print("=" * 70)