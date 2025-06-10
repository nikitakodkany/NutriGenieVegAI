# veg·e·tar·i·an Fitness Recipe Recommender

## Overview

An AI-powered system that provides personalized meal recommendations to help you meet your fitness and nutrition goals. It combines user profile analysis, nutritional calculations, dietary/allergen filtering, and advanced recipe generation using open-source large language models (LLMs).

---

## Features

- **Personalized Nutrition:**  
  Calculates BMI, TDEE, target calories, and recommended macronutrient split based on your profile and fitness goals.

- **Dietary Preferences & Restrictions:**  
  Supports vegetarian, vegan, and other plant-based diets. Handles common allergens and dietary restrictions.

- **AI-Generated Recipes:**  
  Uses [Mistral-7B-Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) to generate new recipes that closely match your calorie and macro targets.

- **Recipe Database & Search:**  
  Integrates with TheMealDB for a wide variety of recipes and uses ChromaDB for fast, vector-based search and retrieval.

- **Nutritional Analysis:**  
  Estimates nutrition for any recipe using ingredient parsing and the USDA FoodData Central API.

- **Modern Frontend:**  
  Streamlit-based UI with a clean, responsive design, profile management, and interactive recipe cards.

- **Backend API:**  
  FastAPI backend with endpoints for nutrition calculation, recipe recommendation, and health checks.

---

## Architecture

```
User (Streamlit UI)
      |
      v
FastAPI Backend
      |
      +---> ChromaDB (Recipe Search/Storage)
      |
      +---> TheMealDB (Recipe Data)
      |
      +---> USDA API (Nutrition Lookup)
      |
      +---> Mistral-7B-Instruct (Recipe Generation)
```

---

## Setup

### 1. Clone the Repository

```sh
git clone https://github.com/nikitakodkany/vegReciperRecommender.git
cd vegReciperRecommender
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Run the Backend

```sh
cd backend/app
uvicorn main:app --reload
```

### 4. Run the Frontend

```sh
cd frontend/src
streamlit run app.py
```

---

## Usage

1. **Open the Streamlit app** (usually at http://localhost:8501).
2. **Fill in your profile:**  
   - Height, weight, age, sex  
   - Activity level  
   - Fitness goal (deficit, maintenance, bulking)  
   - Dietary preference and restrictions/allergens  
   - Number of recipes to generate
3. **Get Recommendations:**  
   - Click "Get AI-Generated Recommendations"
   - View your nutritional profile and personalized recipe suggestions
   - Expand any recipe card to see ingredients, instructions, and nutrition facts

---

## API Endpoints

- `POST /calculate-nutrition`  
  Calculate BMI, TDEE, target calories, and macro split from user profile.

- `POST /recommend-recipes`  
  Get recipe recommendations matching your nutrition targets and preferences.

- `GET /recipe/{recipe_id}`  
  Retrieve a specific recipe by ID.

- `GET /health`  
  Health check endpoint.

- `GET /ready`  
  Readiness check endpoint.

---

## Model & Hardware Requirements

- **Recipe Generation Model:**  
  [Mistral-7B-Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) (loaded via Hugging Face Transformers)
- **Hardware:**  
  - At least 12GB GPU VRAM recommended for float16 inference.
  - CPU inference is possible but slow for a 7B model.

---

## Customization

- **Change the LLM:**  
  Edit `backend/app/core/llama_model.py` and update the model name.
- **Add More Dietary Preferences:**  
  Update the frontend dropdowns and backend filtering logic.
- **Add More Recipe Sources:**  
  Integrate additional APIs or databases in the backend.

---

## Development Notes

- All virtual environments and large files are excluded via `.gitignore`.
- The backend will automatically download the Mistral-7B-Instruct model on first run.
- The system is modular—swap out components as needed for your use case.

---

## Credits

- [Mistral-7B-Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) by Mistral AI
- [Streamlit](https://streamlit.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [ChromaDB](https://www.trychroma.com/)
- [TheMealDB](https://www.themealdb.com/)
- [USDA FoodData Central](https://fdc.nal.usda.gov/)

---

## License

MIT License

---

**Enjoy personalized, AI-powered fitness recipes!** 
