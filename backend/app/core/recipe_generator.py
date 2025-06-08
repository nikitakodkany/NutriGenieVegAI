"""Recipe generation module using LLaMA, TheMealDB, and ChromaDB."""

from typing import List, Dict, Any, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from ..schemas.recipe import RecipeRequest, RecipeResponse
from ..clients.meal_db_client import MealDBClient
from ..db.chroma_client import ChromaRecipeClient
import logging
from datetime import datetime
import threading
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecipeGenerator:
    """Recipe generator using LLaMA, TheMealDB, and ChromaDB."""
    
    def __init__(self):
        """Initialize the recipe generator."""
        try:
            # Initialize clients
            self.meal_db = MealDBClient()
            self.chroma_db = ChromaRecipeClient()
            
            # Initialize model-related attributes
            self._model = None
            self._tokenizer = None
            self._model_loaded = False
            self._model_lock = threading.Lock()
            
            # Initialize ChromaDB in background
            self._init_thread = threading.Thread(target=self._initialize_chroma_db)
            self._init_thread.daemon = True
            self._init_thread.start()
            
            logger.info("RecipeGenerator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RecipeGenerator: {e}")
            raise
    
    def _load_model(self):
        """Lazily load the LLaMA model."""
        if not self._model_loaded:
            with self._model_lock:
                if not self._model_loaded:  # Double-check pattern
                    try:
                        logger.info("Loading LLaMA model...")
                        self._model = AutoModelForCausalLM.from_pretrained(
                            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                            torch_dtype=torch.float16,
                            device_map="auto"
                        )
                        self._tokenizer = AutoTokenizer.from_pretrained(
                            "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
                        )
                        self._model_loaded = True
                        logger.info("LLaMA model loaded successfully")
                    except Exception as e:
                        logger.error(f"Failed to load LLaMA model: {e}")
                        raise
    
    def _initialize_chroma_db(self):
        """Initialize ChromaDB with recipes from TheMealDB in background."""
        try:
            # Get all categories
            categories = self.meal_db.get_categories()
            
            # Load recipes for each category
            for category in categories:
                recipes = self.meal_db.get_recipes_by_category(category)
                for recipe in recipes:
                    try:
                        self.chroma_db.store_recipe(recipe)
                    except Exception as e:
                        logger.warning(f"Failed to store recipe {recipe.get('idMeal')}: {e}")
                        continue
            
            logger.info("ChromaDB initialized with recipes from TheMealDB")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
    
    def is_ready(self) -> bool:
        """Check if the generator is ready to handle requests."""
        return self._init_thread.is_alive() is False
    
    def generate_recipe(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a recipe based on the request.
        
        Args:
            request: Dictionary containing recipe request parameters
                - dietary_preferences: List of dietary preferences
                - dietary_restrictions: List of dietary restrictions
                - ingredients: List of preferred ingredients
                - cuisine: Preferred cuisine type
                - meal_type: Type of meal (breakfast, lunch, dinner, etc.)
                - max_prep_time: Maximum preparation time in minutes
                - max_cook_time: Maximum cooking time in minutes
                - servings: Number of servings
                - difficulty: Difficulty level (easy, medium, hard)
        
        Returns:
            Dict[str, Any]: Generated recipe
            
        Raises:
            ValueError: If request parameters are invalid
            RuntimeError: If recipe generation fails
        """
        try:
            if not request:
                raise ValueError("Request cannot be empty")
            
            # Create search query from request parameters
            query = self._create_search_query(request)
            
            # Try to find matching recipes in ChromaDB
            recipes = self.chroma_db.search_recipes(
                query=query,
                n_results=5,
                dietary_preferences=request.get("dietary_preferences"),
                dietary_restrictions=request.get("dietary_restrictions")
            )
            
            if recipes:
                # Return the best matching recipe
                return recipes[0]
            
            # If no matches found, try LLaMA generation
            try:
                # Load model if not already loaded
                self._load_model()
                
                prompt = self._create_prompt(request)
                inputs = self._tokenizer(prompt, return_tensors="pt").to(self._model.device)
                
                with torch.no_grad():
                    outputs = self._model.generate(
                        **inputs,
                        max_length=512,
                        num_return_sequences=1,
                        temperature=0.7,
                        top_p=0.9,
                        do_sample=True
                    )
                
                generated_text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
                recipe = self._parse_llama_output(generated_text)
                
                # Store the generated recipe in ChromaDB
                self.chroma_db.store_recipe(recipe)
                
                return recipe
                
            except Exception as e:
                logger.warning(f"LLaMA generation failed: {e}")
                # Fallback to random recipe from TheMealDB
                recipe = self.meal_db.get_random_recipe()
                return self.meal_db.convert_to_recipe_response(recipe)
                
        except Exception as e:
            logger.error(f"Recipe generation failed: {e}")
            raise RuntimeError(f"Failed to generate recipe: {str(e)}")
    
    def _create_search_query(self, request: Dict[str, Any]) -> str:
        """Create a search query from request parameters."""
        query_parts = []
        
        if request.get("ingredients"):
            query_parts.extend(request["ingredients"])
        if request.get("cuisine"):
            query_parts.append(request["cuisine"])
        if request.get("meal_type"):
            query_parts.append(request["meal_type"])
        if request.get("difficulty"):
            query_parts.append(request["difficulty"])
            
        return " ".join(query_parts)
    
    def _create_prompt(self, request: Dict[str, Any]) -> str:
        """Create a prompt for LLaMA based on request parameters."""
        prompt = "Generate a recipe with the following requirements:\n"
        
        if request.get("dietary_preferences"):
            prompt += f"Dietary preferences: {', '.join(request['dietary_preferences'])}\n"
        if request.get("dietary_restrictions"):
            prompt += f"Dietary restrictions: {', '.join(request['dietary_restrictions'])}\n"
        if request.get("ingredients"):
            prompt += f"Preferred ingredients: {', '.join(request['ingredients'])}\n"
        if request.get("cuisine"):
            prompt += f"Cuisine: {request['cuisine']}\n"
        if request.get("meal_type"):
            prompt += f"Meal type: {request['meal_type']}\n"
        if request.get("max_prep_time"):
            prompt += f"Maximum preparation time: {request['max_prep_time']} minutes\n"
        if request.get("max_cook_time"):
            prompt += f"Maximum cooking time: {request['max_cook_time']} minutes\n"
        if request.get("servings"):
            prompt += f"Servings: {request['servings']}\n"
        if request.get("difficulty"):
            prompt += f"Difficulty: {request['difficulty']}\n"
            
        prompt += "\nPlease provide a recipe in the following format:\n"
        prompt += "Title: [Recipe Name]\n"
        prompt += "Category: [Category]\n"
        prompt += "Cuisine: [Cuisine]\n"
        prompt += "Servings: [Number]\n"
        prompt += "Prep Time: [Minutes]\n"
        prompt += "Cook Time: [Minutes]\n"
        prompt += "Difficulty: [Easy/Medium/Hard]\n"
        prompt += "Ingredients:\n- [Ingredient 1]\n- [Ingredient 2]\n..."
        prompt += "Instructions:\n1. [Step 1]\n2. [Step 2]\n..."
        prompt += "Nutritional Info:\n- Calories: [Number]\n- Protein: [Number]g\n- Carbs: [Number]g\n- Fat: [Number]g"
        
        return prompt
    
    def _parse_llama_output(self, output: str) -> Dict[str, Any]:
        """Parse LLaMA output into a recipe dictionary."""
        try:
            lines = output.strip().split("\n")
            recipe = {
                "idMeal": str(hash(output)),
                "strMeal": "",
                "strCategory": "",
                "strArea": "",
                "strInstructions": "",
                "strMealThumb": "",
                "ingredients": [],
                "dietary_info": {}
            }
            
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("Title:"):
                    recipe["strMeal"] = line[6:].strip()
                elif line.startswith("Category:"):
                    recipe["strCategory"] = line[9:].strip()
                elif line.startswith("Cuisine:"):
                    recipe["strArea"] = line[8:].strip()
                elif line.startswith("Ingredients:"):
                    current_section = "ingredients"
                elif line.startswith("Instructions:"):
                    current_section = "instructions"
                    recipe["strInstructions"] = ""
                elif line.startswith("- "):
                    if current_section == "ingredients":
                        recipe["ingredients"].append(line[2:].strip())
                elif current_section == "instructions":
                    recipe["strInstructions"] += line + "\n"
            
            # Extract dietary information
            recipe["dietary_info"] = self.chroma_db._extract_dietary_info(recipe, recipe["ingredients"])
            
            return recipe
            
        except Exception as e:
            logger.error(f"Failed to parse LLaMA output: {e}")
            raise ValueError("Invalid recipe format in LLaMA output") 