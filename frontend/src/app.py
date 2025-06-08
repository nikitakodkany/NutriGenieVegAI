import streamlit as st
import requests
import json
from typing import Dict, List
import time

# API configuration
API_URL = "http://localhost:8000"

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
        background-color: #23272f;
        margin-bottom: 1rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    .profile-card {
        background: #23272f;
        border-radius: 12px;
        padding: 0.5rem 1.2rem 1.2rem 1.2rem;
        margin-bottom: 0.5rem;
        margin-top: -1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.10);
    }
    .profile-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #8fd19e;
        margin-bottom: 0.7rem;
        margin-top: 0;
    }
    .profile-section label, .profile-section .stNumberInput, .profile-section .stSelectbox, .profile-section .stMultiSelect {
        font-size: 1.05rem;
    }
    .profile-section hr {
        margin: 1.2rem 0 1.2rem 0;
        border: 0;
        border-top: 1px solid #333;
    }
    .nutri-card {
        background: #23272f;
        border-radius: 12px;
        padding: 1.5rem 1.2rem 1.2rem 1.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.10);
    }
    .nutri-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #8fd19e;
        margin-bottom: 0.7rem;
    }
    .macro-metric {
        font-size: 1.2rem;
        color: #f8f9fa;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .macro-label {
        color: #b5b5b5;
        font-size: 1.05rem;
    }
    .suggestion-card {
        padding: 0.5rem;
        border-radius: 5px;
        background-color: #e6f3ff;
        margin: 0.5rem 0;
    }
    .status-box {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .status-healthy {
        background-color: rgba(40, 167, 69, 0.3);
        box-shadow: 0 0 10px rgba(40, 167, 69, 0.2);
    }
    .status-unhealthy {
        background-color: rgba(220, 53, 69, 0.3);
        box-shadow: 0 0 10px rgba(220, 53, 69, 0.2);
    }
    .sidebar-content {
        padding: 1rem;
    }
    .profile-section {
        margin-top: 2rem;
        padding-top: 1rem;
    }
    /* Reduce Streamlit sidebar container padding (try both selectors for compatibility) */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    .css-1d391kg { /* fallback for older Streamlit versions */
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Check API status
def check_api_status():
    """Check if the API is responsive"""
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "healthy"
        return False
    except requests.RequestException:
        return False

# Initialize session state for API status
if 'api_status' not in st.session_state:
    st.session_state.api_status = check_api_status()

# Sidebar with profile and API status
with st.sidebar:
    st.markdown('<div class="profile-card">', unsafe_allow_html=True)
    st.markdown('<div class="profile-title">Profile & Settings</div>', unsafe_allow_html=True)
    st.markdown('<hr style="margin-top:0.7rem; margin-bottom:1.2rem;">', unsafe_allow_html=True)
    st.markdown('<div class="profile-section">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.1rem; font-weight:600; color:#f8f9fa; margin-bottom:0.5rem;">Your Profile</div>', unsafe_allow_html=True)
    
    height = st.number_input("Height (cm)", min_value=100, max_value=250)
    weight = st.number_input("Weight (kg)", min_value=30, max_value=200)
    age = st.number_input("Age", min_value=18, max_value=100)
    sex = st.selectbox("Sex", ["Male", "Female"]).lower()
    
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

    # Dietary Preferences
    dietary_preference = st.selectbox(
        "Dietary Preference",
        [
            "high-protein vegetarian",
            "high-protein vegan",
            "low-carb vegetarian",
            "keto vegetarian",
            "athlete/bodybuilder plant-based",
            "whole-food plant-based (wfpb)",
            "fruitarian"
        ]
    )
    
    # Dietary Restrictions
    allergies = st.multiselect(
        "Dietary Restrictions",
        [
            "Gluten-Free",
            "Dairy-Free",
            "Nut-Free",
            "Soy-Free",
            "Egg-Free",
            "Shellfish-Free",
            "Fish-Free",
            "Lacto-Vegetarian",
            "Ovo-Vegetarian",
            "Lacto-Ovo Vegetarian"
        ]
    )
    num_recipes = st.number_input("Number of Recipes", min_value=1, max_value=10, value=5)
    st.markdown('</div></div>', unsafe_allow_html=True)

# Main content
st.markdown("<div style='font-size:2.2rem; font-weight:800; color:#f8f9fa; margin-bottom:0.2rem;'>Your Gym Buddy in the Kitchen</div>", unsafe_allow_html=True)
st.markdown("<div style='color:#b5b5b5; font-size:1.15rem; margin-bottom:1.2rem;'>Personalized meals to match your training goals and nutrition targets.</div>", unsafe_allow_html=True)

# Calculate and display results
if st.button("Get AI-Generated Recommendations"):
    if not st.session_state.api_status:
        st.error("API is currently offline. Please try again later.")
    else:
        # Prepare user profile
        user_profile = {
            "height": height,
            "weight": weight,
            "age": age,
            "sex": sex,
            "activity_level": activity_level,
            "fitness_goal": fitness_goal,
            "dietary_preference": dietary_preference,
            "dietary_restrictions": allergies
        }

        try:
            # Calculate nutritional targets
            nutrition_response = requests.post(
                f"{API_URL}/calculate-nutrition",
                json=user_profile
            )
            nutrition_data = nutrition_response.json()

            # Display nutritional profile
            st.markdown("<div class='nutri-card'>", unsafe_allow_html=True)
            st.markdown("<div class='nutri-title'>Your Nutritional Profile</div>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"<div class='macro-label'>BMI</div><div class='macro-metric'>{nutrition_data['bmi']:.1f}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='macro-label'>TDEE</div><div class='macro-metric'>{nutrition_data['tdee']:.0f} kcal</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='macro-label'>Target Calories</div><div class='macro-metric'>{nutrition_data['target_calories']:.0f} kcal</div>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"<div class='macro-label'>Protein Target</div><div class='macro-metric'>{nutrition_data['macro_split']['protein']}g</div>", unsafe_allow_html=True)
            st.markdown("<div class='nutri-title'>Recommended Macronutrient Split</div>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"<div class='macro-label'>Protein</div><div class='macro-metric'>{nutrition_data['macro_split']['protein']}g ({nutrition_data['macro_split']['protein_percent']:.0f}%)</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='macro-label'>Carbs</div><div class='macro-metric'>{nutrition_data['macro_split']['carbs']}g ({nutrition_data['macro_split']['carbs_percent']:.0f}%)</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='macro-label'>Fat</div><div class='macro-metric'>{nutrition_data['macro_split']['fat']}g ({nutrition_data['macro_split']['fat_percent']:.0f}%)</div>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"<div class='macro-label'>Fiber</div><div class='macro-metric'>{nutrition_data['macro_split']['fiber']}g</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Get recipe recommendations
            recipes_response = requests.post(
                f"{API_URL}/recommend-recipes",
                json={
                    "profile": user_profile,
                    "target_calories": int(nutrition_data['target_calories']),
                    "macro_split": nutrition_data['macro_split'],
                    "num_recipes": num_recipes
                }
            )
            try:
                recipes = recipes_response.json()
            except Exception as e:
                st.error(f"Failed to parse recipe response: {e}")
                st.stop()

            st.markdown("<div class='nutri-title'>AI-Generated Recipe Recommendations</div>", unsafe_allow_html=True)
            if not isinstance(recipes, list):
                st.error(f"Recipe API error: {recipes}")
            else:
                for i, recipe in enumerate(recipes):
                    with st.expander(f"{recipe['title']} ({recipe['calories']} kcal)", expanded=False):
                        st.markdown(f"""
                            <div style='background: #23272f; border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 0.5rem; box-shadow: 0 2px 12px rgba(0,0,0,0.10);'>
                                <div style='font-size:1.15rem; font-weight:700; color:#8fd19e; margin-bottom:0.2rem;'>{recipe['title']}</div>
                                <div style='color:#b5b5b5; font-size:1.05rem; margin-bottom:1.1rem;'>({recipe['calories']} kcal)</div>
                                <span style='font-size:1.1rem; color:#8fd19e; font-weight:600;'>Macros:</span><br/>
                                <span style='color:#f8f9fa;'>Protein: <b>{recipe['macros']['protein']}g</b> &nbsp;|&nbsp; Carbs: <b>{recipe['macros']['carbs']}g</b> &nbsp;|&nbsp; Fat: <b>{recipe['macros']['fat']}g</b> &nbsp;|&nbsp; Fiber: <b>{recipe['macros']['fiber']}g</b></span>
                                <hr style='margin: 0.7rem 0 1.1rem 0; border: 0; border-top: 1px solid #333;'>
                                <div style='display: flex; gap: 2.5rem; flex-wrap: wrap;'>
                                    <div style='flex: 1; min-width: 180px;'>
                                        <span style='font-size:1.08rem; color:#f8f9fa; font-weight:600;'>Ingredients</span>
                                        <ul style='padding-left: 1.2rem; margin-bottom: 0;'>
                                            {''.join([f"<li style='margin-bottom: 0.3rem; color: #e0e0e0;'>{(ing['amount'] + ' ' if ing.get('amount') else '') + ing.get('name', str(ing))}</li>" if isinstance(ing, dict) else f"<li style='margin-bottom: 0.3rem; color: #e0e0e0;'>{ing}</li>" for ing in recipe['ingredients']])}
                                        </ul>
                                    </div>
                                    <div style='flex: 2; min-width: 220px;'>
                                        <span style='font-size:1.08rem; color:#f8f9fa; font-weight:600;'>Instructions</span>
                                        <ol style='padding-left: 1.2rem; margin-bottom: 0;'>
                                            {''.join([f"<li style='margin-bottom: 0.7rem; color: #e0e0e0;'>{step}</li>" for step in recipe['steps']])}
                                        </ol>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the API: {str(e)}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Made with ❤️ for fitness-focused vegetarians and vegans</p>
        <p>Powered by LLaMA AI</p>
    </div>
""", unsafe_allow_html=True) 