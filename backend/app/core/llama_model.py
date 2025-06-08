from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import List, Dict, Any
import json
import os

class LLaMAModel:
    def __init__(self):
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        
        # Initialize tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,  # Use half precision for better memory efficiency
            device_map="auto",  # Automatically handle model placement
            low_cpu_mem_usage=True  # Optimize CPU memory usage
        )

    def generate_recipe(self, 
                       dietary_preference: str,
                       target_calories: int,
                       macro_split: Dict[str, float],
                       allergies: List[str] = None) -> Dict[str, Any]:
        """
        Generate a recipe using LLaMA model based on nutritional requirements.
        """
        # Construct the prompt
        prompt = f"""Generate a {dietary_preference} recipe that meets the following nutritional requirements:
        - Target calories: {target_calories} kcal
        - Protein: {macro_split['protein']}g
        - Carbs: {macro_split['carbs']}g
        - Fat: {macro_split['fat']}g
        - Fiber: {macro_split['fiber']}g
        """

        if allergies:
            prompt += f"\nAvoid these ingredients: {', '.join(allergies)}"

        prompt += """
        Please provide the recipe in the following JSON format:
        {
            "title": "Recipe title",
            "ingredients": ["ingredient1", "ingredient2", ...],
            "steps": ["step1", "step2", ...],
            "calories": number,
            "macros": {
                "protein": number,
                "carbs": number,
                "fat": number,
                "fiber": number
            },
            "tags": ["tag1", "tag2", ...]
        }
        """

        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_length=1024,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # Decode and parse response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract JSON from response
        try:
            # Find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            recipe_json = response[json_start:json_end]
            recipe = json.loads(recipe_json)
            return recipe
        except Exception as e:
            print(f"Error parsing recipe: {e}")
            return None

    def generate_recipe_variations(self, 
                                 base_recipe: Dict[str, Any],
                                 num_variations: int = 3) -> List[Dict[str, Any]]:
        """
        Generate variations of a base recipe.
        """
        prompt = f"""Generate {num_variations} variations of this recipe:
        Title: {base_recipe['title']}
        Ingredients: {', '.join(base_recipe['ingredients'])}
        Steps: {' '.join(base_recipe['steps'])}
        
        Keep the same nutritional profile but modify ingredients and steps.
        Provide each variation in the same JSON format as the original recipe.
        """

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_length=2048,
            temperature=0.8,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract variations
        variations = []
        try:
            # Find all JSON objects in the response
            json_objects = []
            start = 0
            while True:
                start = response.find('{', start)
                if start == -1:
                    break
                end = response.find('}', start) + 1
                json_objects.append(response[start:end])
                start = end

            # Parse each JSON object
            for json_str in json_objects:
                try:
                    variation = json.loads(json_str)
                    variations.append(variation)
                except:
                    continue

            return variations[:num_variations]
        except Exception as e:
            print(f"Error parsing variations: {e}")
            return []

    def analyze_recipe_nutrition(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a recipe's nutritional content and provide suggestions for improvement.
        """
        prompt = f"""Analyze this recipe's nutritional content and provide suggestions:
        Title: {recipe['title']}
        Ingredients: {', '.join(recipe['ingredients'])}
        Current macros: {json.dumps(recipe['macros'])}
        
        Provide analysis and suggestions in JSON format:
        {{
            "analysis": "brief analysis of nutritional content",
            "suggestions": ["suggestion1", "suggestion2", ...],
            "improved_macros": {{
                "protein": number,
                "carbs": number,
                "fat": number,
                "fiber": number
            }}
        }}
        """

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_length=1024,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            analysis_json = response[json_start:json_end]
            return json.loads(analysis_json)
        except Exception as e:
            print(f"Error parsing analysis: {e}")
            return None 