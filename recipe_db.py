from typing import List, Dict, Set
import json
import os

class Recipe:
    def __init__(self, title: str, ingredients: List[str], steps: List[str],
                 calories: int, macros: Dict[str, float], tags: List[str]):
        self.title = title
        self.ingredients = ingredients
        self.steps = steps
        self.calories = calories
        self.macros = macros
        self.tags = tags

    def to_dict(self):
        return {
            'title': self.title,
            'ingredients': self.ingredients,
            'steps': self.steps,
            'calories': self.calories,
            'macros': self.macros,
            'tags': self.tags
        }

class RecipeDatabase:
    def __init__(self):
        self.recipes = []
        self._load_sample_recipes()

    def _load_sample_recipes(self):
        # Sample recipes - in a real application, this would come from a database
        self.recipes = [
            Recipe(
                title="High-Protein Tofu Scramble",
                ingredients=[
                    "400g firm tofu",
                    "1 tbsp olive oil",
                    "1 bell pepper, diced",
                    "1 onion, diced",
                    "2 cloves garlic, minced",
                    "1 tsp turmeric",
                    "1 tsp nutritional yeast",
                    "Salt and pepper to taste"
                ],
                steps=[
                    "Press tofu to remove excess water",
                    "Heat oil in a pan over medium heat",
                    "Sauté onion and pepper until soft",
                    "Crumble tofu into the pan",
                    "Add garlic, turmeric, and nutritional yeast",
                    "Cook for 5-7 minutes until heated through",
                    "Season with salt and pepper"
                ],
                calories=320,
                macros={
                    'protein': 28,
                    'carbs': 12,
                    'fat': 18,
                    'fiber': 4
                },
                tags=['high-protein', 'vegan', 'breakfast', 'low-carb']
            ),
            Recipe(
                title="Quinoa Buddha Bowl",
                ingredients=[
                    "1 cup quinoa",
                    "1 can chickpeas",
                    "2 cups mixed greens",
                    "1 avocado",
                    "1 cup roasted vegetables",
                    "2 tbsp tahini",
                    "1 lemon",
                    "Salt and pepper to taste"
                ],
                steps=[
                    "Cook quinoa according to package instructions",
                    "Drain and rinse chickpeas",
                    "Prepare roasted vegetables",
                    "Assemble bowl with quinoa base",
                    "Top with greens, chickpeas, avocado, and vegetables",
                    "Drizzle with tahini and lemon juice",
                    "Season with salt and pepper"
                ],
                calories=450,
                macros={
                    'protein': 18,
                    'carbs': 55,
                    'fat': 22,
                    'fiber': 12
                },
                tags=['balanced', 'vegan', 'lunch', 'high-fiber']
            )
        ]

    def filter_recipes(self, 
                      max_calories: int = None,
                      min_protein: int = None,
                      dietary_preference: str = None,
                      excluded_ingredients: Set[str] = None,
                      tags: List[str] = None) -> List[Recipe]:
        """
        Filter recipes based on various criteria.
        """
        filtered_recipes = self.recipes

        if max_calories:
            filtered_recipes = [r for r in filtered_recipes if r.calories <= max_calories]
        
        if min_protein:
            filtered_recipes = [r for r in filtered_recipes if r.macros['protein'] >= min_protein]
        
        if dietary_preference:
            filtered_recipes = [r for r in filtered_recipes if dietary_preference in r.tags]
        
        if excluded_ingredients:
            filtered_recipes = [
                r for r in filtered_recipes 
                if not any(ingredient.lower() in ' '.join(r.ingredients).lower() 
                          for ingredient in excluded_ingredients)
            ]
        
        if tags:
            filtered_recipes = [
                r for r in filtered_recipes 
                if any(tag in r.tags for tag in tags)
            ]

        return filtered_recipes

    def get_recipe_recommendations(self, 
                                 target_calories: int,
                                 macro_split: Dict[str, float],
                                 dietary_preference: str,
                                 excluded_ingredients: Set[str] = None) -> List[Recipe]:
        """
        Get recipe recommendations based on nutritional goals and preferences.
        """
        # Calculate acceptable ranges for macros (±20%)
        protein_range = (macro_split['protein'] * 0.8, macro_split['protein'] * 1.2)
        carbs_range = (macro_split['carbs'] * 0.8, macro_split['carbs'] * 1.2)
        fat_range = (macro_split['fat'] * 0.8, macro_split['fat'] * 1.2)

        filtered_recipes = self.filter_recipes(
            max_calories=target_calories,
            dietary_preference=dietary_preference,
            excluded_ingredients=excluded_ingredients
        )

        # Score recipes based on how well they match the macro targets
        scored_recipes = []
        for recipe in filtered_recipes:
            score = 0
            if protein_range[0] <= recipe.macros['protein'] <= protein_range[1]:
                score += 1
            if carbs_range[0] <= recipe.macros['carbs'] <= carbs_range[1]:
                score += 1
            if fat_range[0] <= recipe.macros['fat'] <= fat_range[1]:
                score += 1
            
            scored_recipes.append((recipe, score))

        # Sort by score and return top recipes
        scored_recipes.sort(key=lambda x: x[1], reverse=True)
        return [recipe for recipe, score in scored_recipes] 