from pydantic import BaseModel, validator
from typing import List, Optional

class RecipeRequest(BaseModel):
    """Request model for recipe generation"""
    dietary_preference: str
    dietary_restrictions: List[str]
    height: float
    weight: float
    age: int
    sex: str
    activity_level: float
    fitness_goal: str

    @validator('sex', 'fitness_goal', 'dietary_preference', pre=True)
    def lower_case_fields(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

class RecipeResponse(BaseModel):
    """Response model for recipe generation"""
    title: str
    ingredients: List[str]
    instructions: List[str]
    nutritional_info: dict
    preparation_time: int
    cooking_time: int
    servings: int
    difficulty: str
    tags: List[str]

class RecipeRecommendationRequest(BaseModel):
    profile: RecipeRequest
    target_calories: int
    macro_split: dict
    num_recipes: Optional[int] = 5

class RecipeRecommendationResponse(BaseModel):
    """Response model for recipe recommendation"""
    recipes: List[RecipeResponse]
    total_recipes: int
    recommended_calories: int
    macro_split: dict 