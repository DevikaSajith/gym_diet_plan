import pandas as pd
import os

# Mock logic from utils.py to verify
def test_calc(food_name, weight):
    print(f"\nTesting: {food_name}, Weight: {weight}g")
    
    # Read the file directly
    df = pd.read_csv('diet_app/data/calories.csv')
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Clean
    # Check what the raw value is
    raw_match = df[df['fooditem'] == food_name]
    if raw_match.empty:
        # Try search
        raw_match = df[df['fooditem'].str.contains(food_name, case=False, regex=False)]
        
    if raw_match.empty:
        print("Food not found.")
        return

    row = raw_match.iloc[0]
    print(f"Matched Food: {row['fooditem']}")
    print(f"Raw Cals/100g string: '{row['cals_per100grams']}'")
    
    # Simulate cleaning
    cal_str = str(row['cals_per100grams']).replace("cal", "").strip()
    try:
        val_per_100 = float(cal_str)
        print(f"Parsed Value (kcal/100g): {val_per_100}")
        
        cal_per_gram = val_per_100 / 100
        total = cal_per_gram * weight
        print(f"Total for {weight}g: {total} kcal")
    except ValueError as e:
        print(f"Error parsing: {e}")

# Run for a few items
test_calc("Chicken Biryani", 200)
test_calc("Apple", 150)
