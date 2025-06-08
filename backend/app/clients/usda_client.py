import requests
import logging
from typing import Optional, Dict
import re
from functools import lru_cache

USDA_API_KEY = "xo5teH0J5kW2VDcLNS0Uuac3k4evSi0sTuTf0AsL"
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

logger = logging.getLogger(__name__)

# Simple unit to grams conversion (approximate, for common kitchen units)
UNIT_TO_GRAMS = {
    "g": 1,
    "gram": 1,
    "grams": 1,
    "kg": 1000,
    "kilogram": 1000,
    "kilograms": 1000,
    "mg": 0.001,
    "milligram": 0.001,
    "milligrams": 0.001,
    "lb": 453.6,
    "pound": 453.6,
    "pounds": 453.6,
    "oz": 28.35,
    "ounce": 28.35,
    "ounces": 28.35,
    "cup": 240,
    "cups": 240,
    "tbsp": 15,
    "tablespoon": 15,
    "tablespoons": 15,
    "tsp": 5,
    "teaspoon": 5,
    "teaspoons": 5,
    "pinch": 0.36,
    "clove": 5,
    "cloves": 5,
    "slice": 30,
    "slices": 30,
    "piece": 50,
    "pieces": 50,
    "large": 50,
    "medium": 30,
    "small": 15
}

class USDAClient:
    def __init__(self, api_key: str = USDA_API_KEY):
        self.api_key = api_key

    @lru_cache(maxsize=512)
    def get_nutrition(self, ingredient_name: str) -> Optional[Dict[str, float]]:
        """
        Search for an ingredient and return per-100g nutrition info (calories, protein, carbs, fat, fiber).
        """
        params = {
            "api_key": self.api_key,
            "query": ingredient_name,
            "pageSize": 1
        }
        try:
            resp = requests.get(USDA_SEARCH_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("foods"):
                return None
            food = data["foods"][0]
            nutrients = {n["nutrientName"].lower(): n["value"] for n in food.get("foodNutrients", [])}
            # Map USDA names to our keys
            return {
                "calories": nutrients.get("energy", 0),
                "protein": nutrients.get("protein", 0),
                "carbs": nutrients.get("carbohydrate, by difference", 0),
                "fat": nutrients.get("total lipid (fat)", 0),
                "fiber": nutrients.get("fiber, total dietary", 0)
            }
        except Exception as e:
            logger.warning(f"USDA lookup failed for {ingredient_name}: {e}")
            return None

    @staticmethod
    def estimate_grams(ingredient: Dict) -> float:
        """
        Estimate the weight in grams for an ingredient dict (amount, unit).
        Defaults to 100g if unknown.
        """
        amount = ingredient.get("amount", "1")
        unit = ingredient.get("unit", "").lower().strip()
        # Try to parse amount as a float (handle fractions like '1/2')
        try:
            if isinstance(amount, (int, float)):
                amt = float(amount)
            elif isinstance(amount, str):
                amt = float(sum([float(eval(part)) for part in re.split(r'\s+', amount)]))
            else:
                amt = 1.0
        except Exception:
            amt = 1.0
        # Convert unit to grams
        grams_per_unit = UNIT_TO_GRAMS.get(unit, None)
        if grams_per_unit:
            return amt * grams_per_unit
        # If unit is missing but ingredient is a common item (e.g., "egg"), use a default
        if unit == "" and ingredient.get("name", "").lower() in ["egg", "eggs"]:
            return 50 * amt
        # Fallback
        return 100.0 * amt 