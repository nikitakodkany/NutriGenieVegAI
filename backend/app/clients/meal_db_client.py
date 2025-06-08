"""Client for interacting with TheMealDB API."""

import requests
import logging
from typing import List, Dict, Any, Optional
from ..schemas.recipe import RecipeResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MealDBClient:
    """Client for TheMealDB API."""
    
    BASE_URL = "https://www.themealdb.com/api/json/v1/1"
    
    def __init__(self):
        """Initialize the MealDB client."""
        self.session = requests.Session()
    
    def search_recipe(self, name: str) -> List[Dict[str, Any]]:
        """Search for recipes by name."""
        try:
            response = self.session.get(f"{self.BASE_URL}/search.php", params={"s": name})
            response.raise_for_status()
            data = response.json()
            return data.get("meals", [])
        except Exception as e:
            logger.error(f"Failed to search recipe: {e}")
            return []
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Get recipe details by ID."""
        try:
            response = self.session.get(f"{self.BASE_URL}/lookup.php", params={"i": recipe_id})
            response.raise_for_status()
            data = response.json()
            meals = data.get("meals", [])
            return meals[0] if meals else None
        except Exception as e:
            logger.error(f"Failed to get recipe by ID: {e}")
            return None
    
    def get_random_recipe(self) -> Optional[Dict[str, Any]]:
        """Get a random recipe."""
        try:
            response = self.session.get(f"{self.BASE_URL}/random.php")
            response.raise_for_status()
            data = response.json()
            meals = data.get("meals", [])
            return meals[0] if meals else None
        except Exception as e:
            logger.error(f"Failed to get random recipe: {e}")
            return None
    
    def get_categories(self) -> List[str]:
        """Get all recipe categories."""
        try:
            response = self.session.get(f"{self.BASE_URL}/categories.php")
            response.raise_for_status()
            data = response.json()
            categories = data.get("categories", [])
            return [cat["strCategory"] for cat in categories]
        except Exception as e:
            logger.error(f"Failed to get categories: {e}")
            return []
    
    def get_recipes_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get recipes by category."""
        try:
            response = self.session.get(f"{self.BASE_URL}/filter.php", params={"c": category})
            response.raise_for_status()
            data = response.json()
            return data.get("meals", [])
        except Exception as e:
            logger.error(f"Failed to get recipes by category: {e}")
            return []
    
    def convert_to_recipe_response(self, meal: Dict[str, Any]) -> Dict[str, Any]:
        """Convert meal data to RecipeResponse format."""
        if not meal:
            return {}
            
        # Extract ingredients and measurements
        ingredients = []
        for i in range(1, 21):  # TheMealDB supports up to 20 ingredients
            ingredient = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ingredient and ingredient.strip():
                ingredients.append({
                    "name": ingredient.strip(),
                    "amount": measure.strip() if measure else "",
                    "unit": ""
                })
        
        # Extract instructions
        instructions = meal.get("strInstructions", "").split("\n")
        instructions = [step.strip() for step in instructions if step.strip()]
        
        # Create recipe response
        return {
            "idMeal": meal.get("idMeal", ""),
            "strMeal": meal.get("strMeal", ""),
            "strCategory": meal.get("strCategory", ""),
            "strArea": meal.get("strArea", ""),
            "strInstructions": instructions,
            "strMealThumb": meal.get("strMealThumb", ""),
            "ingredients": ingredients,
            "dietary_info": {
                "vegetarian": False,  # Default values, can be updated based on ingredients
                "vegan": False,
                "gluten_free": False,
                "dairy_free": False
            }
        } 