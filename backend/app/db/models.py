from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    ingredients = Column(JSON)
    steps = Column(JSON)
    calories = Column(Integer)
    macros = Column(JSON)
    tags = Column(JSON)
    dietary_type = Column(String)  # 'vegetarian' or 'vegan'
    embedding = Column(JSON)  # Store recipe embeddings for similarity search

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "ingredients": self.ingredients,
            "steps": self.steps,
            "calories": self.calories,
            "macros": self.macros,
            "tags": self.tags,
            "dietary_type": self.dietary_type
        }

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    height = Column(Float)
    weight = Column(Float)
    age = Column(Integer)
    sex = Column(String)
    activity_level = Column(Float)
    fitness_goal = Column(String)
    dietary_preference = Column(String)
    allergies = Column(JSON)
    tdee = Column(Float)
    target_calories = Column(Float)
    macro_split = Column(JSON)

    def to_dict(self):
        return {
            "id": self.id,
            "height": self.height,
            "weight": self.weight,
            "age": self.age,
            "sex": self.sex,
            "activity_level": self.activity_level,
            "fitness_goal": self.fitness_goal,
            "dietary_preference": self.dietary_preference,
            "allergies": self.allergies,
            "tdee": self.tdee,
            "target_calories": self.target_calories,
            "macro_split": self.macro_split
        } 