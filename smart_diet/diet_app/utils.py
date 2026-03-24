import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean
from collections import Counter
import os
from django.conf import settings

# Load data once or on demand
DATA_DIR = os.path.join(settings.BASE_DIR, 'diet_app', 'data')

def get_diet_recommendation(user_data):
    csv_path = os.path.join(DATA_DIR, 'diet_recommendations_dataset.csv')
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return {"error": "Dataset not found"}

    # Clean the dataset
    df['Disease_Type'] = df['Disease_Type'].fillna('None')
    df['Allergies'] = df['Allergies'].fillna('None')
    df['Dietary_Restrictions'] = df['Dietary_Restrictions'].fillna('None')

    # Mappings
    gender_map = {'Male': 0, 'Female': 1}
    activity_map = {'Sedentary': 0, 'Moderate': 1, 'Active': 2}
    disease_map = {'None': 0, 'Obesity': 1, 'Diabetes': 2, 'Hypertension': 3}
    allergy_map = {'None': 0, 'Peanuts': 1, 'Gluten': 2}
    cuisine_map = {'Mexican': 0, 'Chinese': 1, 'Italian': 2, 'Indian': 3}

    # Encode
    df['Gender_enc'] = df['Gender'].map(gender_map)
    df['Activity_enc'] = df['Physical_Activity_Level'].map(activity_map)
    df['Disease_enc'] = df['Disease_Type'].map(disease_map)
    df['Allergies_enc'] = df['Allergies'].map(allergy_map)
    df['Cuisine_enc'] = df['Preferred_Cuisine'].map(cuisine_map)

    features = [
        'Age', 'BMI', 'Weekly_Exercise_Hours', 'Gender_enc', 
        'Activity_enc', 'Disease_enc', 'Allergies_enc', 'Cuisine_enc'
    ]
    
    # Normalize
    df_norm = df[features].copy()
    # Simple Min-Max normalization
    for col in features:
        min_val = df[col].min()
        max_val = df[col].max()
        if max_val - min_val == 0:
            df_norm[col] = 0
        else:
            df_norm[col] = (df[col] - min_val) / (max_val - min_val)

    # Process User Data
    age = user_data['age']
    gender = user_data['gender']
    weight = user_data['weight']
    height = user_data['height']
    disease = user_data['disease']
    activity = user_data['activity']
    allergies = user_data['allergies']
    cuisine = user_data['cuisine']
    if cuisine == 'Any':
        cuisine = 'Mexican' # Default
    exercise_hours = user_data.get('exercise_hours', 4.0)

    bmi = weight / ((height / 100) ** 2)

    # Encode user
    gender_enc = gender_map.get(gender, 0)
    activity_enc = activity_map.get(activity, 1)
    disease_enc = disease_map.get(disease, 0)
    allergies_enc = allergy_map.get(allergies, 0)
    cuisine_enc = cuisine_map.get(cuisine, 0)

    # User vector
    user_vector = np.array([age, bmi, exercise_hours, gender_enc, activity_enc, disease_enc, allergies_enc, cuisine_enc])
    user_norm = user_vector.astype(float)

    # Normalize user vector using dataset stats
    # Be careful with manual normalization logic to match df_norm
    cols = ['Age', 'BMI', 'Weekly_Exercise_Hours', 'Gender_enc', 'Activity_enc', 'Disease_enc', 'Allergies_enc', 'Cuisine_enc']
    # Re-calculate min/max from df to normalize user
    for i, col in enumerate(cols):
        min_val = df[col].min()
        max_val = df[col].max()
        if max_val - min_val != 0:
            user_norm[i] = (user_norm[i] - min_val) / (max_val - min_val)
        else:
            user_norm[i] = 0

    distances = []
    for idx, row in df_norm.iterrows():
        dist = euclidean(row.values, user_norm)
        diet = df.loc[idx, 'Diet_Recommendation']
        distances.append((dist, diet))

    distances.sort(key=lambda x: x[0])
    top_matches = distances[:10]
    recommendations = [diet for _, diet in top_matches]
    if not recommendations:
        return {"result": "Balanced", "reasoning": "Could not find similarity, defaulting to Balanced.", "top_matches": []}

    top_diets = Counter(recommendations).most_common(3)
    best_diet = top_diets[0][0]

    goal = user_data.get('goal', 'Maintain')

    reasoning = ""
    if best_diet == "Low_Carb":
        reasoning = "Best suited for diabetes or high blood glucose management."
    elif best_diet == "Low_Sodium":
        reasoning = "Recommended for hypertension or high blood pressure."
    else:
        reasoning = "General healthy diet, suitable for weight maintenance or obesity without complications."

    # Adjust reasoning based on goal
    if goal == "Weight Loss":
        reasoning += " To support your Weight Loss goal, ensure a calorie deficit and prioritize high-protein, high-fiber foods."
    elif goal == "Weight Gain":
        reasoning += " To support Weight Gain, increase your calorie intake with nutrient-dense foods and healthy fats."
    elif goal == "Build Muscle":
        reasoning += " For Building Muscle, focus on high-protein intake and consistent strength training."

    return {
        "result": best_diet,
        "bmi": round(bmi, 1),
        "reasoning": reasoning,
        "top_matches": [(d, round(s, 3)) for s, d in top_matches[:5]],
        "other_options": [d for d, count in top_diets[1:]] # Pass other top diets
    }

def get_calorie_prediction(food_name, weight_grams):
    csv_path = os.path.join(DATA_DIR, 'calories.csv')
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return None, "Dataset not found"

    # Clean column names
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Process 'cals_per100grams'
    if 'cals_per100grams' in df.columns:
        df["cals_per100grams"] = df["cals_per100grams"].astype(str)
        df["cals_per100grams"] = df["cals_per100grams"].str.replace("cal", "", regex=False)
        df["cals_per100grams"] = df["cals_per100grams"].str.strip()
        df["cals_per100grams"] = pd.to_numeric(df["cals_per100grams"], errors="coerce")
        df["cal_per_gram"] = df["cals_per100grams"] / 100
    else:
        return None, "Column 'cals_per100grams' not found in dataset"

    df["fooditem"] = df["fooditem"].astype(str).str.strip().str.lower()
    food_name = food_name.strip().lower()

    if food_name not in df["fooditem"].values:
        # Try partial match if exact match fails
        matches = df[df["fooditem"].str.contains(food_name, regex=False)]
        
        if not matches.empty:
             # Return list of potential matches
             suggestions = matches["fooditem"].unique().tolist()
             # Limit to top 10 to avoid overwhelming
             return None, None, suggestions[:10]
        
        return None, f"Food '{food_name}' not found.", []

    cal_pg = df[df["fooditem"] == food_name]["cal_per_gram"].values[0]
    total_cal = cal_pg * weight_grams
    return total_cal, None, []
