# VRR: Fitness Recipe Recommender

## Overview
VRR is a fitness recipe recommender system that provides personalized meal recommendations based on your nutritional goals, dietary preferences, and restrictions. It features:
- FastAPI backend
- ChromaDB for recipe storage and retrieval
- Streamlit frontend
- AI-powered recipe generation using open-source LLMs

## Recipe Generation Model
**Now powered by [Mistral-7B-Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2)!**

- The backend uses the `mistralai/Mistral-7B-Instruct-v0.2` model from Hugging Face for generating new recipes that match your macro and calorie targets.
- Model is loaded via Hugging Face Transformers.
- **Hardware requirements:**
  - At least 12GB GPU VRAM recommended for float16 inference.
  - For best performance, use a modern NVIDIA GPU (e.g., RTX 3060/3070/3080/4090 or A100).
  - CPU inference is possible but very slow for a 7B model.

## Setup
1. **Clone the repository:**
   ```sh
   git clone https://github.com/nikitakodkany/vegReciperRecommender.git
   cd vegReciperRecommender
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Run the backend:**
   ```sh
   cd backend/app
   uvicorn main:app --reload
   ```
4. **Run the frontend:**
   ```sh
   cd frontend/src
   streamlit run app.py
   ```

## Notes
- The backend will automatically download and load the Mistral-7B-Instruct model on first run (requires internet connection).
- If you want to use a different model, update the model name in `backend/app/core/llama_model.py`.
- Make sure your `.gitignore` excludes all virtual environments and large files.

## Credits
- [Mistral-7B-Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2) by Mistral AI
- [Streamlit](https://streamlit.io/), [FastAPI](https://fastapi.tiangolo.com/), [ChromaDB](https://www.trychroma.com/)

---

# Enjoy personalized, AI-powered fitness recipes! 