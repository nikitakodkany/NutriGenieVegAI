from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from typing import List

# Initialize the model and tokenizer
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)

def get_recipe_embedding(text: str) -> List[float]:
    """
    Generate an embedding for a recipe or query text using the sentence transformer model.
    """
    # Tokenize the text
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt", max_length=512)
    
    # Generate embeddings
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Use mean pooling to get a single vector
    token_embeddings = outputs.last_hidden_state
    attention_mask = inputs['attention_mask']
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    embedding = torch.sum(token_embeddings * input_mask_expanded, 0) / torch.clamp(input_mask_expanded.sum(0), min=1e-9)
    
    # Convert to numpy array and normalize
    embedding = embedding.numpy()
    embedding = embedding / np.linalg.norm(embedding)
    
    return embedding.tolist()

def get_recipe_similarity(recipe1: str, recipe2: str) -> float:
    """
    Calculate the cosine similarity between two recipes.
    """
    embedding1 = get_recipe_embedding(recipe1)
    embedding2 = get_recipe_embedding(recipe2)
    
    # Calculate cosine similarity
    similarity = np.dot(embedding1, embedding2)
    return float(similarity) 