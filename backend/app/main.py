"""Main FastAPI application for VRR"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import psutil
import torch
from datetime import datetime
import chromadb
import logging
import re

from .db.chroma_client import ChromaRecipeClient
from .core.calculations import calculate_bmi, calculate_tdee, calculate_target_calories, calculate_macro_split
from .core.llama_model import LLaMAModel
from .schemas.recipe import RecipeRequest, RecipeResponse, RecipeRecommendationRequest
from .core.recipe_generator import RecipeGenerator
from .clients.meal_db_client import MealDBClient
from .clients.usda_client import USDAClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VRR API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChromaDB
chroma_client = ChromaRecipeClient()

# Initialize clients
llama_model = LLaMAModel()
recipe_generator = RecipeGenerator()
meal_db_client = MealDBClient()
usda_client = USDAClient()

# Pydantic models for request/response
class UserProfile(BaseModel):
    height: float
    weight: float
    age: int
    sex: str
    activity_level: float
    fitness_goal: str
    dietary_preference: str
    dietary_restrictions: List[str]

class RecipeAnalysis(BaseModel):
    analysis: str
    suggestions: List[str]
    improved_macros: Dict[str, float]

@app.post("/calculate-nutrition")
async def calculate_nutrition(profile: UserProfile):
    """Calculate nutritional targets based on user profile."""
    try:
        bmi = calculate_bmi(profile.height, profile.weight)
        tdee = calculate_tdee(
            profile.height,
            profile.weight,
            profile.age,
            profile.sex,
            profile.activity_level
        )
        target_calories = calculate_target_calories(tdee, profile.fitness_goal)
        macro_split = calculate_macro_split(target_calories, profile.fitness_goal)

        return {
            "bmi": bmi,
            "tdee": tdee,
            "target_calories": target_calories,
            "macro_split": macro_split
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-recipe", response_model=RecipeResponse)
async def generate_recipe(request: RecipeRequest):
    """Generate a recipe based on user preferences and restrictions"""
    try:
        # Check if service is ready
        if not recipe_generator.is_ready():
            raise HTTPException(
                status_code=503,
                detail="Service is still initializing. Please try again in a few moments."
            )
        
        # Convert request to dictionary
        request_dict = request.dict()
        
        # Generate recipe
        recipe = recipe_generator.generate_recipe(request_dict)
        
        # Convert to response model
        return RecipeResponse(**recipe)
    except ValueError as e:
        logger.error(f"Invalid request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Recipe generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recipe-variations/{recipe_id}")
async def get_recipe_variations(recipe_id: str, num_variations: int = 3):
    """Generate variations of an existing recipe."""
    try:
        base_recipe = chroma_client.get_recipe(recipe_id)
        if not base_recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        variations = llama_model.generate_recipe_variations(
            base_recipe=base_recipe,
            num_variations=num_variations
        )
        
        return variations
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-recipe/{recipe_id}")
async def analyze_recipe(recipe_id: str) -> RecipeAnalysis:
    """Analyze a recipe's nutritional content and provide suggestions."""
    try:
        recipe = chroma_client.get_recipe(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        analysis = llama_model.analyze_recipe_nutrition(recipe)
        if not analysis:
            raise HTTPException(status_code=500, detail="Failed to analyze recipe")
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/recommend-recipes")
async def recommend_recipes(request: RecipeRecommendationRequest):
    profile = request.profile
    target_calories = request.target_calories
    macro_split = request.macro_split
    try:
        # Create a search query based on user preferences
        search_query = f"{profile.dietary_preference} recipe with {target_calories} calories"
        
        # Search for recipes in the database
        results = chroma_client.search_recipes(
            query=search_query,
            n_results=5,
            dietary_preferences=[profile.dietary_preference] if profile.dietary_preference else None,
            dietary_restrictions=profile.dietary_restrictions if hasattr(profile, 'dietary_restrictions') and profile.dietary_restrictions else None
        )
        
        # If no results found, try generating a new recipe
        if not results:
            generated_recipe = recipe_generator.generate_recipe({
                "dietary_preference": profile.dietary_preference,
                "target_calories": target_calories,
                "macro_split": macro_split,
                "dietary_restrictions": getattr(profile, 'dietary_restrictions', [])
            })
            if generated_recipe:
                results = [generated_recipe]
        
        # Filter out recipes with allergens
        filtered_recipes = []
        for recipe in results:
            # Extract ingredients text safely
            ingredients_text = ""
            if isinstance(recipe.get('ingredients'), list):
                ingredients_text = ' '.join([
                    str(ing.get('name', '')) if isinstance(ing, dict) else str(ing)
                    for ing in recipe['ingredients']
                ])
            elif isinstance(recipe.get('ingredients'), str):
                ingredients_text = recipe['ingredients']
            
            # Check for allergens
            has_allergen = False
            if hasattr(profile, 'dietary_restrictions') and profile.dietary_restrictions:
                has_allergen = any(
                    allergen.lower() in ingredients_text.lower()
                    for allergen in profile.dietary_restrictions
                )
            
            # Fetch full details if missing ingredients or steps
            ingredients = recipe.get('ingredients', [])
            steps = recipe.get('steps', [])
            if (not ingredients or not steps) and (recipe.get('idMeal') or recipe.get('id')):
                recipe_id = recipe.get('idMeal', '') or recipe.get('id', '')
                full_recipe = meal_db_client.get_recipe_by_id(recipe_id)
                if full_recipe:
                    # Use convert_to_recipe_response to get a normalized dict
                    full_recipe = meal_db_client.convert_to_recipe_response(full_recipe)
                    ingredients = full_recipe.get('ingredients', [])
                    # Convert instructions to steps
                    steps = full_recipe.get('strInstructions', [])
                    if isinstance(steps, str):
                        if '\n' in steps:
                            steps = [step.strip() for step in steps.split('\n') if step.strip()]
                        elif '.' in steps:
                            steps = [step.strip() for step in steps.split('.') if step.strip()]
                        else:
                            steps = [steps]
            # Map fields to frontend expectations
            nutrition = recipe.get('nutrition', {})
            tags = recipe.get('tags', [])
            if isinstance(tags, str):
                tags = tags.split(',') if tags else []
            instructions = recipe.get('instructions', [])
            if isinstance(instructions, str):
                if '\n' in instructions:
                    instructions = [step.strip() for step in instructions.split('\n') if step.strip()]
                elif '.' in instructions:
                    instructions = [step.strip() for step in instructions.split('.') if step.strip()]
                else:
                    instructions = [instructions]

            # If missing calories or macros, use USDA to generate them
            calories = nutrition.get('calories', 0) if nutrition else 0
            macros = {
                "protein": nutrition.get("protein", 0),
                "carbs": nutrition.get("carbs", 0),
                "fat": nutrition.get("fat", 0),
                "fiber": nutrition.get("fiber", 0)
            }
            if calories == 0 or all(v == 0 for v in macros.values()):
                try:
                    usda_total = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}
                    for ing in ingredients:
                        name = ing["name"] if isinstance(ing, dict) else str(ing)
                        usda_nutrition = usda_client.get_nutrition(name)
                        grams = usda_client.estimate_grams(ing) if isinstance(ing, dict) else 100.0
                        if usda_nutrition:
                            for k in usda_total:
                                usda_total[k] += float(usda_nutrition[k]) * (grams / 100.0)
                    macros = {k: usda_total[k] for k in ["protein", "carbs", "fat", "fiber"]}
                    calories = usda_total["calories"]
                except Exception as e:
                    logger.warning(f"USDA nutrition generation failed: {e}")

            # Clean up instructions: remove 'STEP X' lines and merge lines that are part of the same step
            def clean_instructions(steps):
                cleaned = []
                buffer = ""
                for step in steps:
                    s = str(step).strip()
                    # Remove lines like 'STEP 1', 'STEP 2', etc.
                    if s.upper().startswith("STEP ") and s[5:].strip().isdigit():
                        continue
                    # Remove leading numbers like '1. ', '2. ', etc.
                    s = re.sub(r'^\d+\.\s*', '', s)
                    # Merge lines that are part of the same step (if previous line didn't end with a period)
                    if buffer and not buffer.strip().endswith('.'):
                        buffer += ' ' + s
                    else:
                        if buffer:
                            cleaned.append(buffer.strip())
                        buffer = s
                if buffer:
                    cleaned.append(buffer.strip())
                return [c for c in cleaned if c]

            steps = clean_instructions(steps)

            recipe_data = {
                "id": recipe.get('idMeal', '') or recipe.get('id', ''),
                "title": recipe.get('strMeal', '') or recipe.get('name', ''),
                "ingredients": ingredients,
                "steps": steps,
                "macros": macros,
                "calories": calories,
                "tags": tags,
                "image": recipe.get('strMealThumb', '') or recipe.get('image', ''),
                "source": recipe.get('source', 'TheMealDB'),
            }
            if not has_allergen:
                filtered_recipes.append(recipe_data)
        
        # After building filtered_recipes, filter and sort by closeness to target macros/calories
        def within_50kcal_5g(value, target, macro=False):
            if target == 0:
                return True
            if macro:
                return abs(value - target) <= 5
            else:
                return abs(value - target) <= 50

        def nutrition_distance(recipe, target_macros, target_calories):
            return (
                abs(recipe['calories'] - target_calories) +
                abs(recipe['macros']['protein'] - target_macros['protein']) +
                abs(recipe['macros']['carbs'] - target_macros['carbs']) +
                abs(recipe['macros']['fat'] - target_macros['fat'])
            )

        # Only keep recipes within ±50 kcal and ±5g of all macro targets
        close_recipes = [
            r for r in filtered_recipes
            if within_50kcal_5g(r['calories'], target_calories, macro=False)
            and within_50kcal_5g(r['macros']['protein'], macro_split['protein'], macro=True)
            and within_50kcal_5g(r['macros']['carbs'], macro_split['carbs'], macro=True)
            and within_50kcal_5g(r['macros']['fat'], macro_split['fat'], macro=True)
        ]
        # If none are close, fall back to all
        if not close_recipes:
            close_recipes = filtered_recipes
        # Sort by distance to target
        close_recipes.sort(key=lambda r: nutrition_distance(r, macro_split, target_calories))
        # Return top num_recipes
        num_recipes = getattr(request, 'num_recipes', 5)
        return close_recipes[:num_recipes]
    except Exception as e:
        logger.error(f"Recipe recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recipe/{recipe_id}")
async def get_recipe(recipe_id: str):
    """Get a specific recipe by ID."""
    recipe = chroma_client.get_recipe(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # Check if recipe generator is ready
        is_ready = recipe_generator.is_ready()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available": memory.available
            },
            "services": {
                "recipe_generator": {
                    "status": "ready" if is_ready else "initializing",
                    "model_loaded": recipe_generator._model_loaded if hasattr(recipe_generator, '_model_loaded') else False
                }
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    if not recipe_generator.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Service is still initializing. Please try again in a few moments."
        )
    return {"status": "ready"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 