import streamlit as st
import pandas as pd
from utils import calculate_bmi, calculate_tdee, calculate_target_calories, calculate_macro_split
from recipe_db import RecipeDatabase

# Set page config
st.set_page_config(
    page_title="Fitness Recipe Recommender",
    page_icon="🥗",
    layout="wide"
)

# Initialize recipe database
recipe_db = RecipeDatabase()

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .recipe-card {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("🥗 Fitness Recipe Recommender")
st.markdown("""
    Get personalized vegetarian/vegan recipe recommendations based on your fitness goals,
    dietary preferences, and nutritional needs.
""")

# User Input Section
st.header("Your Profile")

col1, col2 = st.columns(2)

with col1:
    height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
    weight = st.number_input("Weight (kg)", min_value=30, max_value=200, value=70)
    age = st.number_input("Age", min_value=18, max_value=100, value=30)
    sex = st.selectbox("Sex", ["Male", "Female"])

with col2:
    activity_level = st.selectbox(
        "Activity Level",
        [
            ("Sedentary (little or no exercise)", 1.2),
            ("Lightly active (light exercise 1-3 days/week)", 1.375),
            ("Moderately active (moderate exercise 3-5 days/week)", 1.55),
            ("Very active (hard exercise 6-7 days/week)", 1.725),
            ("Extra active (very hard exercise & physical job)", 1.9)
        ],
        format_func=lambda x: x[0]
    )[1]

    fitness_goal = st.selectbox(
        "Fitness Goal",
        ["deficit", "maintenance", "bulking"]
    )

    dietary_preference = st.selectbox(
        "Dietary Preference",
        ["vegetarian", "vegan"]
    )

# Allergies and restrictions
st.subheader("Dietary Restrictions")
allergies = st.multiselect(
    "Select any allergies or ingredients to avoid",
    ["Nuts", "Gluten", "Soy", "Dairy", "Eggs", "Shellfish", "Fish"]
)

# Calculate and display results
if st.button("Get Recommendations"):
    # Calculate metrics
    bmi = calculate_bmi(height, weight)
    tdee = calculate_tdee(height, weight, age, sex, activity_level)
    target_calories = calculate_target_calories(tdee, fitness_goal)
    macro_split = calculate_macro_split(target_calories, fitness_goal)

    # Display results
    st.header("Your Nutritional Profile")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("BMI", f"{bmi:.1f}")
    with col2:
        st.metric("TDEE", f"{tdee:.0f} kcal")
    with col3:
        st.metric("Target Calories", f"{target_calories:.0f} kcal")
    with col4:
        st.metric("Protein Target", f"{macro_split['protein']}g")

    # Display macro split
    st.subheader("Recommended Macronutrient Split")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Protein", f"{macro_split['protein']}g ({macro_split['protein_percent']:.0f}%)")
    with col2:
        st.metric("Carbs", f"{macro_split['carbs']}g ({macro_split['carbs_percent']:.0f}%)")
    with col3:
        st.metric("Fat", f"{macro_split['fat']}g ({macro_split['fat_percent']:.0f}%)")
    with col4:
        st.metric("Fiber", f"{macro_split['fiber']}g")

    # Get recipe recommendations
    recommendations = recipe_db.get_recipe_recommendations(
        target_calories=target_calories,
        macro_split=macro_split,
        dietary_preference=dietary_preference,
        excluded_ingredients=set(allergies)
    )

    # Display recommendations
    st.header("Recommended Recipes")
    
    for recipe in recommendations:
        with st.expander(f"🍽️ {recipe.title} ({recipe.calories} kcal)"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Ingredients")
                for ingredient in recipe.ingredients:
                    st.write(f"• {ingredient}")
                
                st.subheader("Instructions")
                for i, step in enumerate(recipe.steps, 1):
                    st.write(f"{i}. {step}")
            
            with col2:
                st.subheader("Nutrition Facts")
                st.write(f"Calories: {recipe.calories} kcal")
                st.write(f"Protein: {recipe.macros['protein']}g")
                st.write(f"Carbs: {recipe.macros['carbs']}g")
                st.write(f"Fat: {recipe.macros['fat']}g")
                st.write(f"Fiber: {recipe.macros['fiber']}g")
                
                st.subheader("Tags")
                for tag in recipe.tags:
                    st.write(f"#{tag}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Made with ❤️ for fitness-focused vegetarians and vegans</p>
    </div>
""", unsafe_allow_html=True) 