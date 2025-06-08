import numpy as np
from typing import Dict

def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """Calculate BMI given height in cm and weight in kg."""
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)

def calculate_tdee(height_cm: float, weight_kg: float, age: int, sex: str, activity_level: float) -> float:
    """
    Calculate TDEE using Mifflin-St Jeor equation.
    
    Activity levels:
    1.2 - Sedentary (little or no exercise)
    1.375 - Lightly active (light exercise 1-3 days/week)
    1.55 - Moderately active (moderate exercise 3-5 days/week)
    1.725 - Very active (hard exercise 6-7 days/week)
    1.9 - Extra active (very hard exercise & physical job)
    """
    # Convert height to cm if needed
    height_cm = float(height_cm)
    weight_kg = float(weight_kg)
    age = float(age)
    
    # Mifflin-St Jeor Equation
    if sex.lower() == 'male':
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    return bmr * activity_level

def calculate_target_calories(tdee: float, goal: str) -> float:
    """Calculate target daily calories based on fitness goal."""
    if goal == 'deficit':
        return tdee - 500
    elif goal == 'maintenance':
        return tdee
    elif goal == 'bulking':
        return tdee + 500
    else:
        raise ValueError("Invalid goal. Must be 'deficit', 'maintenance', or 'bulking'")

def calculate_macro_split(target_calories: float, goal: str) -> Dict[str, float]:
    """
    Calculate recommended macronutrient split based on fitness goal.
    Returns: Dictionary with protein, carbs, fat, and fiber in grams and percentages
    """
    if goal == 'deficit':
        # High protein, moderate carbs, low fat
        protein_percent = 0.40
        carbs_percent = 0.40
        fat_percent = 0.20
    elif goal == 'maintenance':
        # Balanced split
        protein_percent = 0.30
        carbs_percent = 0.45
        fat_percent = 0.25
    else:  # bulking
        # Higher carbs, moderate protein, moderate fat
        protein_percent = 0.30
        carbs_percent = 0.50
        fat_percent = 0.20
    
    # Calculate grams (4 calories per gram for protein and carbs, 9 for fat)
    protein_g = (target_calories * protein_percent) / 4
    carbs_g = (target_calories * carbs_percent) / 4
    fat_g = (target_calories * fat_percent) / 9
    
    # Recommended fiber intake (14g per 1000 calories)
    fiber_g = (target_calories / 1000) * 14
    
    return {
        'protein': round(protein_g),
        'carbs': round(carbs_g),
        'fat': round(fat_g),
        'fiber': round(fiber_g),
        'protein_percent': protein_percent * 100,
        'carbs_percent': carbs_percent * 100,
        'fat_percent': fat_percent * 100
    } 