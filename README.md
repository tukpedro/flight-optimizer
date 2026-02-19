# Flight Optimizer

Find the best value flight by price per kilometer ($/km).

## Quick Start

```bash
# Install
pip install -r requirements.txt
cd frontend && npm install && cd ..

# CLI
./flight-optimizer --from London --to Paris Berlin Madrid

# Web App
cd backend && python manage.py runserver    # Terminal 1
cd frontend && npm run dev                   # Terminal 2
# Open http://localhost:5173
```

## Tests

```bash
pytest tests/ -v
```

## Tech Stack

- **Backend:** Python, Django, Django REST Framework
- **Frontend:** React, TypeScript, Vite
- **API:** Kiwi.com Tequila API
