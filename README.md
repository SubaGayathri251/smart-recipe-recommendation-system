# 🍳 Smart Recipe Recommendation System

A **Smart Recipe Recommendation System** built using **Python, Flask, MySQL, and Machine Learning**.

The system recommends recipes based on the ingredients available to the user and preferences such as cuisine, meal type, diet type, cooking time, calories, and protein.

It uses a **hybrid recommendation approach** that combines **rule-based scoring** and a **Random Forest Machine Learning model** to rank recipes.

---

## ✨ Features

- 🥕 Recommend recipes based on available ingredients
- 🌍 Filter recipes by cuisine
- 🍽️ Filter recipes by meal type
- 🥗 Filter recipes by diet type
- ⏱️ Consider maximum cooking time
- 🔥 Consider maximum calories
- 💪 Consider minimum protein
- 🤖 Random Forest Machine Learning model for recipe scoring
- 📊 Hybrid recommendation using Rule-Based and ML scores
- 👩‍🍳 Displays recipe preparation instructions
- ▶️ Provides YouTube search links for cooking videos
- ✅ Shows ingredients already available to the user
- ❌ Shows missing ingredients required for the recipe
- ⭐ Displays recipe ratings and nutritional information

---

## 🛠️ Technologies Used

### Frontend

- HTML
- CSS

### Backend

- Python
- Flask

### Database

- MySQL

### Machine Learning

- Scikit-learn
- Random Forest

### Libraries

- Pandas
- NumPy
- MySQL Connector

---

# 🧠 Recommendation Approach

The system uses a **Hybrid Recommendation Method**.

It combines:

1. Rule-Based Recommendation
2. Machine Learning Prediction

The final recipes are ranked using a **Hybrid Score**.

---

## 📊 Rule-Based Scoring

Recipes are scored based on:

- Ingredient match
- Cuisine preference
- Meal type
- Diet type
- Cooking time
- Calories
- Protein
- Recipe rating

The rule-based scoring uses the following weights:

| Factor | Weight |
|---|---:|
| 🥕 Ingredient Match | 40% |
| 🌍 Cuisine Match | 15% |
| 🥗 Diet Match | 10% |
| 🍽️ Meal Match | 10% |
| ⏱️ Cooking Time | 8% |
| 🔥 Calories | 5% |
| 💪 Protein | 5% |
| ⭐ Rating | 7% |

The total rule-based score is calculated using these weighted factors.

---

## 🤖 Machine Learning

A **Random Forest Machine Learning model** is used to predict a recipe score.

The model uses the following features:

- Total cooking time
- Number of steps
- Number of ingredients
- Calories
- Protein
- Carbohydrates
- Average rating
- Rating count

The trained model is used along with the rule-based recommendation system.

---

## 🔀 Hybrid Score

The final recommendation score is calculated by combining the Rule-Based Score and Machine Learning Score.

```text
Hybrid Score =
(60% × Rule-Based Score)
+
(40% × Machine Learning Score)
```

Recipes are sorted in descending order based on the Hybrid Score.

The top recommended recipes are then displayed to the user.

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/SubaGayathri251/Smart-Recipe-Recommendation-System.git
```

## 2. Move into the Project Folder

```bash
cd Smart-Recipe-Recommendation-System
```

## 3. Install Required Packages

```bash
pip install -r requirements.txt
```

---

# 🗄️ Database Configuration

Create a MySQL database:

```sql
CREATE DATABASE recipe_recommendation;
```

Create a file named `config.py` in the project folder.

Add your MySQL configuration:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "recipe_recommendation",
    "port": 3306
}
```

Replace:

```text
YOUR_MYSQL_PASSWORD
```

with your own MySQL password.

> ⚠️ `config.py` is included in `.gitignore` to protect database credentials.

---

# 📊 Dataset

The project uses recipe and user interaction data containing information such as:

- Recipe names
- Ingredients
- Cooking instructions
- Nutritional information
- Cooking time
- Recipe ratings
- User interactions

The dataset is preprocessed before being imported into the MySQL database.

The preprocessing process includes cleaning and preparing recipe information for recommendation and Machine Learning.

---

# 🚀 Running the Application

Run the Flask application:

```bash
python app.py
```

The application will start on:

```text
http://127.0.0.1:5000
```

Open the above address in your browser.

Then:

1. Enter the ingredients you have available.
2. Select your preferred cuisine.
3. Select the meal type.
4. Select the diet type.
5. Optionally provide cooking time, calorie, and protein preferences.
6. Click **Find New Recipes**.

The system will display the top recommended recipes.

---

# 📋 Example Recommendation

### User Input

```text
Ingredients: Rice
Cuisine: Indian
Meal Type: Dinner
Diet: Vegetarian
```

### Example System Output

The system may recommend recipes such as:

- Green Peas Pulao
- Indian Creamy Rice Pudding (Phirni)

Each recommendation includes:

- 📊 Hybrid recommendation score
- 🤖 Machine Learning score
- 📈 Rule-Based score
- 🥕 Ingredient match percentage
- 🌍 Cuisine
- 🍽️ Meal type
- 🥗 Diet type
- ⏱️ Cooking time
- 🔥 Calories
- 💪 Protein
- ⭐ Rating
- ✅ Available ingredients
- ❌ Missing ingredients
- 👩‍🍳 Preparation instructions
- ▶️ YouTube cooking video search link

---

# 👩‍🍳 Recipe Preparation Support

The system not only recommends recipes but also helps users understand how to prepare them.

For each recommended recipe, the application displays:

- Preparation instructions from the dataset
- Improved step formatting using a keyword-based approach
- A YouTube search link for finding relevant cooking videos

This feature is useful for users who may not know how to prepare a particular recipe.

---

# 📁 Project Structure

```text
Smart-Recipe-Recommendation-System/
│
├── app.py
├── recommendation_engine.py
├── ml_model.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│   ├── raw/
│   └── processed/
│
├── models/
│   └── recipe_recommendation_model.pkl
│
├── scripts/
│   ├── preprocess.py
│   ├── import_data.py
│   ├── build_ingredients.py
│   ├── train_ml_model.py
│   └── test_db.py
│
├── static/
│   └── css/
│       └── style.css
│
└── templates/
    ├── index.html
    └── recommendations.html
```

> Note: Large dataset and model files may not be included in the repository.

---

# ⚠️ Limitations

- Recommendation speed may depend on the dataset size and database query performance.
- Processing a large number of candidate recipes can increase recommendation time.
- Recipe instructions in the original dataset may not always contain properly separated cooking steps.
- A keyword-based approach is used to improve the display of preparation instructions.
- Ingredient matching is primarily based on text matching and normalization.
- Recommendations depend on the quality, completeness, and accuracy of the dataset.
- Some recipe categories or metadata may contain `Unknown` values depending on the available dataset information.

---

# 🔮 Future Improvements

- 👤 User login and personalized recommendations
- ❤️ Save favorite recipes
- 🖼️ Add recipe images
- 🧠 Improved NLP-based recipe instruction processing
- ⚡ Faster database searching and indexing
- 🥕 Advanced ingredient similarity matching
- ⭐ User ratings and feedback system
- 📱 Mobile-responsive interface improvements
- 📝 Allow users to add and share their own recipes
- 🎯 Personalized recommendations based on previous user activity

---

# 📌 How the System Works

```text
User Input
    │
    ▼
Available Ingredients + User Preferences
    │
    ▼
MySQL Candidate Recipe Filtering
    │
    ▼
Ingredient Matching and Preference Scoring
    │
    ├──────────────► Rule-Based Score
    │
    └──────────────► Random Forest ML Score
                         │
                         ▼
                    Hybrid Score
                         │
                         ▼
                 Recipe Ranking
                         │
                         ▼
              Top Recommended Recipes
                         │
                         ▼
       Instructions + Missing Ingredients
                         │
                         ▼
               YouTube Cooking Search
```

---

## 👩‍💻 Author

**Suba Gayathri P**

Final Year B.E. Computer Science and Engineering Student

---

⭐ If you found this project useful, consider giving the repository a star!