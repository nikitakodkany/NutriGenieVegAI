"""ChromaDB client for recipe storage and retrieval."""

import chromadb
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaRecipeClient:
    """Client for managing recipes in ChromaDB."""
    
    def __init__(self):
        """Initialize the ChromaDB client."""
        try:
            self.client = chromadb.PersistentClient(path="data/chroma")
            self.collection = self.client.get_or_create_collection(
                name="recipes",
                metadata={"description": "Recipe collection for VRR"}
            )
            self._cache = {}
            self._cache_expiry = {}
            logger.info("ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
    
    def _check_cache(self, key: str) -> Optional[Any]:
        """Check if a key exists in cache and is not expired."""
        if key in self._cache:
            if datetime.now() < self._cache_expiry[key]:
                return self._cache[key]
            else:
                del self._cache[key]
                del self._cache_expiry[key]
        return None
    
    def _update_cache(self, key: str, value: Any, expiry_minutes: int = 30):
        """Update cache with a new value and expiry time."""
        self._cache[key] = value
        self._cache_expiry[key] = datetime.now() + timedelta(minutes=expiry_minutes)
    
    def _invalidate_cache(self, key: str = None):
        """Invalidate cache for a specific key or all keys."""
        if key:
            if key in self._cache:
                del self._cache[key]
                del self._cache_expiry[key]
        else:
            self._cache.clear()
            self._cache_expiry.clear()
    
    def store_recipe(self, recipe: Dict[str, Any]) -> bool:
        """Store a recipe in ChromaDB."""
        try:
            if not recipe or "idMeal" not in recipe:
                raise ValueError("Invalid recipe data")
            
            # Check if recipe already exists
            existing_recipe = self.get_recipe(recipe["idMeal"])
            if existing_recipe:
                logger.info(f"Recipe {recipe['idMeal']} already exists in database")
                return True
            
            # Create document text from recipe
            doc_text = f"""
            Title: {recipe.get('strMeal', '')}
            Category: {recipe.get('strCategory', '')}
            Area: {recipe.get('strArea', '')}
            Instructions: {recipe.get('strInstructions', '')}
            Tags: {recipe.get('strTags', '')}
            Ingredients: {', '.join([ing['name'] for ing in recipe.get('ingredients', [])])}
            """
            
            # Store in ChromaDB
            self.collection.add(
                ids=[recipe["idMeal"]],
                documents=[doc_text],
                metadatas=[recipe]
            )
            
            # Invalidate cache
            self._invalidate_cache()
            
            logger.info(f"Recipe {recipe['idMeal']} stored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store recipe: {e}")
            raise RuntimeError(f"Failed to store recipe: {str(e)}")
    
    def get_recipe(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """Get a recipe by ID."""
        try:
            # Check cache first
            cache_key = f"recipe_{recipe_id}"
            cached_recipe = self._check_cache(cache_key)
            if cached_recipe:
                return cached_recipe
            
            # Query ChromaDB
            result = self.collection.get(
                ids=[recipe_id],
                include=["metadatas"]
            )
            
            if result and result["metadatas"]:
                recipe = result["metadatas"][0]
                self._update_cache(cache_key, recipe)
                return recipe
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get recipe: {e}")
            return None
    
    def search_recipes(
        self,
        query: str,
        n_results: int = 5,
        dietary_preferences: List[str] = None,
        dietary_restrictions: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for recipes based on query and dietary requirements."""
        try:
            # Check cache first
            cache_key = f"search_{query}_{n_results}_{dietary_preferences}_{dietary_restrictions}"
            cached_results = self._check_cache(cache_key)
            if cached_results:
                return cached_results
            
            # Query ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results * 2  # Get more results for filtering
            )
            
            if not results or not results["metadatas"]:
                return []
            
            # Filter results based on dietary requirements
            filtered_results = []
            for recipe in results["metadatas"][0]:
                if self._meets_dietary_requirements(
                    recipe,
                    dietary_preferences,
                    dietary_restrictions
                ):
                    filtered_results.append(recipe)
                    if len(filtered_results) >= n_results:
                        break
            
            self._update_cache(cache_key, filtered_results)
            return filtered_results
            
        except Exception as e:
            logger.error(f"Failed to search recipes: {e}")
            return []
    
    def _meets_dietary_requirements(
        self,
        recipe: Dict[str, Any],
        dietary_preferences: List[str] = None,
        dietary_restrictions: List[str] = None
    ) -> bool:
        """Check if a recipe meets dietary requirements."""
        if not dietary_preferences and not dietary_restrictions:
            return True
        
        # Get recipe's dietary info
        dietary_info = recipe.get("dietary_info", {})
        
        # Check dietary preferences
        if dietary_preferences:
            if "vegetarian" in dietary_preferences and not dietary_info.get("vegetarian", False):
                return False
            if "vegan" in dietary_preferences and not dietary_info.get("vegan", False):
                return False
        
        # Check dietary restrictions
        if dietary_restrictions:
            if "gluten_free" in dietary_restrictions and not dietary_info.get("gluten_free", False):
                return False
            if "dairy_free" in dietary_restrictions and not dietary_info.get("dairy_free", False):
                return False
        
        return True
    
    def get_all_recipes(self) -> List[Dict[str, Any]]:
        """Get all recipes from ChromaDB."""
        try:
            # Check cache first
            cache_key = "all_recipes"
            cached_recipes = self._check_cache(cache_key)
            if cached_recipes:
                return cached_recipes
            
            # Query ChromaDB
            results = self.collection.get(
                include=["metadatas"]
            )
            
            if not results or not results["metadatas"]:
                return []
            
            recipes = results["metadatas"]
            self._update_cache(cache_key, recipes)
            return recipes
            
        except Exception as e:
            logger.error(f"Failed to get all recipes: {e}")
            return [] 