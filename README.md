# Fitness Recipe Recommender

A personalized recipe recommendation system for fitness-focused vegetarians and vegans. This application helps users choose meals aligned with their fitness goals while respecting their dietary preferences, macronutrient needs, and allergies.

## Features

- BMI and TDEE calculation
- Personalized calorie targets based on fitness goals (deficit, maintenance, bulking)
- Customized macronutrient recommendations
- Vegetarian and vegan recipe filtering
- Allergy and dietary restriction handling
- Detailed recipe information including ingredients, steps, and nutritional facts
- Vector-based recipe search using ChromaDB
- FastAPI backend with Streamlit frontend

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── core/
│   │   │   │   ├── calculations.py
│   │   │   │   └── embeddings.py
│   │   │   ├── db/
│   │   │   │   ├── models.py
│   │   │   │   └── chroma_client.py
│   │   │   └── main.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       └── app.py
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fitness-recipe-recommender.git
cd fitness-recipe-recommender
```

2. Create and activate virtual environments for both backend and frontend:
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. In a new terminal, start the frontend:
```bash
cd frontend
streamlit run src/app.py
```

3. Open your web browser and navigate to the Streamlit URL (typically http://localhost:8501)

4. Enter your personal information:
   - Height and weight
   - Age and sex
   - Activity level
   - Fitness goal
   - Dietary preference
   - Any allergies or restrictions

5. Click "Get Recommendations" to receive personalized recipe suggestions

## Technical Details

The application uses:
- FastAPI for the backend API
- Streamlit for the web interface
- ChromaDB for vector-based recipe search
- Sentence Transformers for recipe embeddings
- SQLAlchemy for database models
- Pandas for data handling
- Custom algorithms for nutritional calculations

## API Endpoints

- `POST /calculate-nutrition`: Calculate nutritional targets based on user profile
- `POST /recommend-recipes`: Get recipe recommendations based on user profile and nutritional targets
- `GET /recipe/{recipe_id}`: Get a specific recipe by ID

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 