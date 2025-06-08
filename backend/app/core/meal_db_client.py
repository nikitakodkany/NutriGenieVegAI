"""TheMealDB API client for VRR"""

import requests
from typing import List, Dict, Any, Optional
from ..schemas.recipe import RecipeResponse

class MealDBClient:
    """Client for interacting with TheMealDB API"""
    
    BASE_URL = "https://www.themealdb.com/api/json/v1/1"
    
    def __init__(self):
        """Initialize the MealDB client"""
        self.session = requests.Session()
    
    def search_recipe(self, query: str) -> List[Dict[str, Any]]:
        """Search for recipes by name
        
        Args:
            query: Recipe name to search for
            
        Returns:
            List of recipe dictionaries
        """
        response = self.session.get(f"{self.BASE_URL}/search.php", params={"s": query})
        response.raise_for_status()
        data = response.json()
        return data.get("meals", [])
    
    def get_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Get recipe details by ID
        
        Args:
            recipe_id: TheMealDB recipe ID
            
        Returns:
            Recipe dictionary if found, None otherwise
        """
        response = self.session.get(f"{self.BASE_URL}/lookup.php", params={"i": recipe_id})
        response.raise_for_status()
        data = response.json()
        meals = data.get("meals", [])
        return meals[0] if meals else None
    
    def get_random_recipe(self) -> Dict[str, Any]:
        """Get a random recipe
        
        Returns:
            Random recipe dictionary
        """
        response = self.session.get(f"{self.BASE_URL}/random.php")
        response.raise_for_status()
        data = response.json()
        return data["meals"][0]
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all recipe categories
        
        Returns:
            List of category dictionaries
        """
        response = self.session.get(f"{self.BASE_URL}/categories.php")
        response.raise_for_status()
        data = response.json()
        return data.get("categories", [])
    
    def get_recipes_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get recipes by category
        
        Args:
            category: Category name
            
        Returns:
            List of recipe dictionaries
        """
        response = self.session.get(f"{self.BASE_URL}/filter.php", params={"c": category})
        response.raise_for_status()
        data = response.json()
        return data.get("meals", [])
    
    def convert_to_recipe_response(self, meal: Dict[str, Any]) -> RecipeResponse:
        """Convert TheMealDB meal to RecipeResponse
        
        Args:
            meal: TheMealDB meal dictionary
            
        Returns:
            RecipeResponse object
        """
        # Extract ingredients and measurements
        ingredients = []
        for i in range(1, 21):  # TheMealDB has up to 20 ingredients
            ingredient = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ingredient and ingredient.strip():
                ingredients.append(f"{measure.strip() if measure else ''} {ingredient.strip()}")
        
        # Split instructions into steps
        instructions = [step.strip() for step in meal["strInstructions"].split(".") if step.strip()]
        
        return RecipeResponse(
            title=meal["strMeal"],
            ingredients=ingredients,
            instructions=instructions,
            nutritional_info={
                "calories": 0,  # TheMealDB doesn't provide nutritional info
                "protein": 0,
                "carbs": 0,
                "fat": 0
            },
            preparation_time=0,  # TheMealDB doesn't provide time info
            cooking_time=0,
            servings=4,  # Default value
            difficulty="Medium",  # Default value
            tags=[meal["strCategory"], meal["strArea"]] if meal.get("strCategory") and meal.get("strArea") else []
        ) 